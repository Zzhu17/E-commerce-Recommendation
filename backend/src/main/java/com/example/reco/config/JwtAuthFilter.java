package com.example.reco.config;

import com.example.reco.service.JwtAuthService;
import com.example.reco.service.RateLimitStore;
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

  public JwtAuthFilter(SecurityProperties properties, JwtAuthService jwtAuthService, RateLimitStore rateLimitStore) {
    this.properties = properties;
    this.jwtAuthService = jwtAuthService;
    this.rateLimitStore = rateLimitStore;
  }

  @Override
  protected boolean shouldNotFilter(HttpServletRequest request) {
    String path = request.getRequestURI();
    return path != null && (path.equals("/api/health") || path.equals("/api/version"));
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
    response.setStatus(allowed ? HttpStatus.UNAUTHORIZED.value() : HttpStatus.TOO_MANY_REQUESTS.value());
    response.setContentType("application/json");
    response.getWriter().write("{\"code\":\"AUTH_FAILED\",\"message\":\"authentication failed\"}");
  }
}
