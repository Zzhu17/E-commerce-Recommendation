package com.example.reco.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.springframework.http.HttpStatus;
import org.springframework.web.filter.OncePerRequestFilter;

public class RateLimitFilter extends OncePerRequestFilter {
  private final RateLimitProperties properties;
  private final com.example.reco.service.RateLimitStore rateLimitStore;

  public RateLimitFilter(RateLimitProperties properties, com.example.reco.service.RateLimitStore rateLimitStore) {
    this.properties = properties;
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

    String key = request.getRemoteAddr();
    Object auth = request.getAttribute(JwtAuthFilter.ATTR_AUTH_CONTEXT);
    if (auth instanceof AuthContext context && context.subject() != null && !context.subject().isBlank()) {
      key = "sub:" + context.subject();
    }
    if (key == null || key.isBlank()) {
      key = "unknown";
    }

    boolean allowed = rateLimitStore.allow(key, properties.getLimit(), properties.getWindowSeconds());
    if (!allowed) {
      response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
      response.setContentType("application/json");
      response.getWriter().write("{\"code\":\"RATE_LIMITED\",\"message\":\"too many requests\"}");
      return;
    }

    filterChain.doFilter(request, response);
  }
}
