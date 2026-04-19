package com.example.reco.config;

import com.example.reco.service.RateLimitStore;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Locale;
import java.util.regex.Pattern;
import org.springframework.http.HttpStatus;
import org.springframework.web.filter.OncePerRequestFilter;

public class GatewayProtectionFilter extends OncePerRequestFilter {
  private static final int WINDOW_SECONDS = 60;

  private final GatewayProtectionProperties properties;
  private final RateLimitStore rateLimitStore;

  public GatewayProtectionFilter(GatewayProtectionProperties properties, RateLimitStore rateLimitStore) {
    this.properties = properties;
    this.rateLimitStore = rateLimitStore;
  }

  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
      throws ServletException, IOException {
    if (!properties.isEnabled()) {
      filterChain.doFilter(request, response);
      return;
    }

    String path = request.getRequestURI() == null ? "" : request.getRequestURI().toLowerCase(Locale.ROOT);
    String query = request.getQueryString() == null ? "" : request.getQueryString().toLowerCase(Locale.ROOT);
    String userAgent = request.getHeader("User-Agent") == null
        ? "unknown"
        : request.getHeader("User-Agent").toLowerCase(Locale.ROOT);
    String remoteIp = request.getRemoteAddr() == null ? "unknown" : request.getRemoteAddr();

    String banKey = "gw:ban:ip:" + remoteIp;
    if (!rateLimitStore.allow(banKey, 1, properties.getBanSeconds())) {
      reject(response, HttpStatus.FORBIDDEN, "BANNED", "request denied");
      return;
    }

    if (isBlocked(userAgent, properties.getBlockedUserAgents()) || isBlocked(path + "?" + query, properties.getBlockedPathPatterns())) {
      rateLimitStore.allow(banKey, 0, properties.getBanSeconds());
      reject(response, HttpStatus.FORBIDDEN, "WAF_BLOCKED", "request denied");
      return;
    }

    if (!rateLimitStore.allow("gw:ratelimit:ip:" + remoteIp, properties.getIpRateLimitPerMinute(), WINDOW_SECONDS)
        || !rateLimitStore.allow("gw:ratelimit:ua:" + userAgent, properties.getUserAgentRateLimitPerMinute(), WINDOW_SECONDS)) {
      reject(response, HttpStatus.TOO_MANY_REQUESTS, "RATE_LIMITED", "too many requests");
      return;
    }

    filterChain.doFilter(request, response);
  }

  private boolean isBlocked(String value, java.util.List<String> patterns) {
    for (String raw : patterns) {
      if (raw == null || raw.isBlank()) {
        continue;
      }
      Pattern p = Pattern.compile(raw, Pattern.CASE_INSENSITIVE);
      if (p.matcher(value).find()) {
        return true;
      }
    }
    return false;
  }

  private void reject(HttpServletResponse response, HttpStatus status, String code, String message) throws IOException {
    response.setStatus(status.value());
    response.setContentType("application/json");
    response.getWriter().write("{\"code\":\"" + code + "\",\"message\":\"" + message + "\"}");
  }
}
