package com.example.reco.service;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;

import com.example.reco.config.AuthContext;
import com.example.reco.config.JwtAuthFilter;
import com.example.reco.config.SecurityProperties;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.web.server.ResponseStatusException;

class AdminAccessServiceTest {
  private final SecurityProperties properties = new SecurityProperties();
  private final SecurityMonitoringService securityMonitoringService = mock(SecurityMonitoringService.class);
  private final AdminAccessService service = new AdminAccessService(properties, securityMonitoringService);

  @Test
  void deniesRequestWithoutAuthContext() {
    MockHttpServletRequest request = new MockHttpServletRequest();
    assertThrows(ResponseStatusException.class, () -> service.requireReadRole(request));
  }

  @Test
  void deniesWriteWhenOnlyReadRole() {
    MockHttpServletRequest request = new MockHttpServletRequest();
    request.setAttribute(
        JwtAuthFilter.ATTR_AUTH_CONTEXT,
        new AuthContext("u1", Set.of(properties.getReadOpsRole()))
    );
    assertThrows(ResponseStatusException.class, () -> service.requireWriteRole(request));
  }
}
