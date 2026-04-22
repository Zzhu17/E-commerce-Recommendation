package com.example.reco.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.example.reco.service.RateLimitStore;
import com.example.reco.service.SecurityMonitoringService;
import jakarta.servlet.ServletException;
import java.io.IOException;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockFilterChain;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

class GatewayProtectionFilterTest {
  @Test
  void allowsRepeatedCleanRequestsWithoutTriggeringBan() throws ServletException, IOException {
    RateLimitStore store = mock(RateLimitStore.class);
    SecurityMonitoringService monitoring = mock(SecurityMonitoringService.class);
    GatewayProtectionFilter filter = new GatewayProtectionFilter(properties(), store, monitoring);

    MockHttpServletRequest request = baseRequest("Mozilla/5.0");
    MockHttpServletResponse first = new MockHttpServletResponse();
    MockHttpServletResponse second = new MockHttpServletResponse();

    when(store.isBlocked("gw:ban:ip:127.0.0.1")).thenReturn(false);
    when(store.allow("gw:ratelimit:ip:127.0.0.1", 120, 60)).thenReturn(true);
    when(store.allow("gw:ratelimit:ua:mozilla/5.0", 300, 60)).thenReturn(true);

    filter.doFilter(request, first, new MockFilterChain());
    filter.doFilter(request, second, new MockFilterChain());

    assertEquals(200, first.getStatus());
    assertEquals(200, second.getStatus());
    verify(store, never()).block("gw:ban:ip:127.0.0.1", 900);
  }

  @Test
  void blocksAndBansBlockedUserAgent() throws ServletException, IOException {
    RateLimitStore store = mock(RateLimitStore.class);
    SecurityMonitoringService monitoring = mock(SecurityMonitoringService.class);
    GatewayProtectionFilter filter = new GatewayProtectionFilter(properties(), store, monitoring);

    MockHttpServletRequest request = baseRequest("sqlmap");
    MockHttpServletResponse response = new MockHttpServletResponse();

    when(store.isBlocked("gw:ban:ip:127.0.0.1")).thenReturn(false);

    filter.doFilter(request, response, new MockFilterChain());

    assertEquals(403, response.getStatus());
    verify(store).block("gw:ban:ip:127.0.0.1", 900);
  }

  private GatewayProtectionProperties properties() {
    GatewayProtectionProperties properties = new GatewayProtectionProperties();
    properties.setBlockedUserAgents(List.of("sqlmap"));
    properties.setBlockedPathPatterns(List.of("\\.git"));
    return properties;
  }

  private MockHttpServletRequest baseRequest(String userAgent) {
    MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/recommendations");
    request.setRemoteAddr("127.0.0.1");
    request.addHeader("User-Agent", userAgent);
    return request;
  }
}
