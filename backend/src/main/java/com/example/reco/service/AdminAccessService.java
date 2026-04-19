package com.example.reco.service;

import com.example.reco.config.AuthContext;
import com.example.reco.config.JwtAuthFilter;
import com.example.reco.config.SecurityProperties;
import jakarta.servlet.http.HttpServletRequest;
import java.util.Set;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class AdminAccessService {
  private final SecurityProperties properties;

  public AdminAccessService(SecurityProperties properties) {
    this.properties = properties;
  }

  public AuthContext currentAuth(HttpServletRequest request) {
    Object value = request.getAttribute(JwtAuthFilter.ATTR_AUTH_CONTEXT);
    if (value instanceof AuthContext context) {
      return context;
    }
    throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "authentication failed");
  }

  public void requireReadRole(HttpServletRequest request) {
    AuthContext auth = currentAuth(request);
    if (!hasAny(auth.roles(), properties.getReadOpsRole(), properties.getWriteOpsRole(), properties.getPlatformAdminRole())) {
      throw new ResponseStatusException(HttpStatus.FORBIDDEN, "forbidden");
    }
  }

  public void requireWriteRole(HttpServletRequest request) {
    AuthContext auth = currentAuth(request);
    if (!hasAny(auth.roles(), properties.getWriteOpsRole(), properties.getPlatformAdminRole())) {
      throw new ResponseStatusException(HttpStatus.FORBIDDEN, "forbidden");
    }
  }

  public void requirePlatformAdmin(HttpServletRequest request) {
    AuthContext auth = currentAuth(request);
    if (!hasAny(auth.roles(), properties.getPlatformAdminRole())) {
      throw new ResponseStatusException(HttpStatus.FORBIDDEN, "forbidden");
    }
  }

  private boolean hasAny(Set<String> roles, String... required) {
    for (String role : required) {
      if (roles.contains(role)) {
        return true;
      }
    }
    return false;
  }
}
