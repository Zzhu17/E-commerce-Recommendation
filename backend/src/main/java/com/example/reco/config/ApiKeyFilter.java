package com.example.reco.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.springframework.http.HttpStatus;
import org.springframework.web.filter.OncePerRequestFilter;

public class ApiKeyFilter extends OncePerRequestFilter {
  private final SecurityProperties properties;

  public ApiKeyFilter(SecurityProperties properties) {
    this.properties = properties;
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

    String path = request.getRequestURI();
    boolean isAdmin = path != null && path.startsWith("/api/admin");
    String header = isAdmin ? properties.getAdminHeader() : properties.getHeader();
    String expected = isAdmin ? properties.getAdminValue() : properties.getValue();

    String provided = request.getHeader(header);
    if (provided == null || expected == null || expected.isBlank() || !provided.equals(expected)) {
      response.setStatus(HttpStatus.UNAUTHORIZED.value());
      response.setContentType("application/json");
      response.getWriter().write("{\"code\":\"UNAUTHORIZED\",\"message\":\"invalid api key\"}");
      return;
    }

    filterChain.doFilter(request, response);
  }
}
