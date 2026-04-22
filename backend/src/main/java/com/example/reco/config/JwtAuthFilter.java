package com.example.reco.config;

import com.example.reco.service.JwtAuthService;
import com.example.reco.service.RateLimitStore;
import com.example.reco.service.SecurityMonitoringService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.springframework.http.HttpStatus;
import org.springframework.web.filter.OncePerRequestFilter;

public class JwtAuthFilter extends OncePerRequestFilter {
  public static final String ATTR_AUTH_CONTEXT = "auth.context";
  private final SecurityProperties properties;
  private final JwtAuthService jwtAuthService;
  private final RateLimitStore rateLimitStore;
  private final SecurityMonitoringService securityMonitoringService;

  public JwtAuthFilter(
      SecurityProperties properties,
      JwtAuthService jwtAuthService,
      RateLimitStore rateLimitStore,
      SecurityMonitoringService securityMonitoringService) {
    this.properties = properties;
    this.jwtAuthService = jwtAuthService;
    this.rateLimitStore = rateLimitStore;
    this.securityMonitoringService = securityMonitoringService;
  }

  @Override
  protected boolean shouldNotFilter(HttpServletRequest request) {
    String path = request.getRequestURI();
    return isPublicPath(path);
  }

  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
      throws ServletException, IOException {
    if (!properties.isEnabled()) {
      filterChain.doFilter(request, response);
      return;
    }

    AuthContext context = jwtAuthService.verifyBearerToken(request.getHeader("Authorization"));
    if (context == null) {
      rejectAuthFailure(request, response);
      return;
    }
    if (isProtectedActuatorPath(request.getRequestURI()) && !hasOpsAccess(context)) {
      securityMonitoringService.recordForbidden(request.getRequestURI());
      FilterErrorResponseWriter.write(response, HttpStatus.FORBIDDEN, "AUTH_FORBIDDEN", "forbidden");
      return;
    }
    request.setAttribute(ATTR_AUTH_CONTEXT, context);
    filterChain.doFilter(request, response);
  }

  private void rejectAuthFailure(HttpServletRequest request, HttpServletResponse response) throws IOException {
    String remote = request.getRemoteAddr() == null ? "unknown" : request.getRemoteAddr();
    String path = request.getRequestURI() == null ? "unknown" : request.getRequestURI();
    String key = "auth-fail:" + remote + ":" + path;
    boolean allowed = rateLimitStore.allow(
        key,
        properties.getAuthFailureLimit(),
        properties.getAuthFailureWindowSeconds()
    );
    boolean rejectedByLimit = !allowed;
    securityMonitoringService.recordAuthFailure(path, remote);
    String code = rejectedByLimit ? "RATE_LIMITED" : "AUTH_FAILED";
    String message = rejectedByLimit ? "too many requests" : "authentication failed";
    FilterErrorResponseWriter.write(
        response,
        rejectedByLimit ? HttpStatus.TOO_MANY_REQUESTS : HttpStatus.UNAUTHORIZED,
        code,
        message
    );
  }

  private boolean isPublicPath(String path) {
    return path != null && (
        path.equals("/api/health")
            || path.equals("/api/version")
            || path.startsWith("/actuator/health")
            || path.equals("/actuator/info"));
  }

  private boolean isProtectedActuatorPath(String path) {
    return path != null && path.startsWith("/actuator/") && !isPublicPath(path);
  }

  private boolean hasOpsAccess(AuthContext context) {
    return context.roles().contains(properties.getReadOpsRole())
        || context.roles().contains(properties.getWriteOpsRole())
        || context.roles().contains(properties.getPlatformAdminRole());
  }
}
