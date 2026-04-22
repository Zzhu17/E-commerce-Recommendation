package com.example.reco.config;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;

import com.example.reco.service.JwtAuthService;
import com.example.reco.service.RateLimitStore;
import com.example.reco.service.SecurityMonitoringService;
import org.junit.jupiter.api.Test;

class FilterConfigTest {
  private final FilterConfig config = new FilterConfig();

  @Test
  void protectsActuatorWithAuthAndRateLimitFilters() {
    var jwtBean = config.jwtAuthFilter(
        new SecurityProperties(),
        mock(JwtAuthService.class),
        mock(RateLimitStore.class),
        mock(SecurityMonitoringService.class)
    );
    var rateLimitBean = config.rateLimitFilter(new RateLimitProperties(), mock(RateLimitStore.class));

    assertTrue(jwtBean.getUrlPatterns().contains("/actuator/*"));
    assertTrue(rateLimitBean.getUrlPatterns().contains("/actuator/*"));
  }
}
