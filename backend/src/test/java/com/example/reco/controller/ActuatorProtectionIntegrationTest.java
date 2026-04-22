package com.example.reco.controller;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.reco.config.JwtAuthFilter;
import com.example.reco.config.RequestIdFilter;
import com.example.reco.config.SecurityProperties;
import com.example.reco.service.JwtAuthService;
import com.example.reco.service.RateLimitStore;
import com.example.reco.service.SecurityMonitoringService;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

class ActuatorProtectionIntegrationTest {
  @Test
  void actuatorPrometheusIsNotAccessibleWithoutAuth() throws Exception {
    SecurityProperties properties = new SecurityProperties();
    properties.setJwtSecret("test-secret");
    RateLimitStore rateLimitStore = Mockito.mock(RateLimitStore.class);
    Mockito.when(rateLimitStore.allow(Mockito.anyString(), Mockito.anyInt(), Mockito.anyInt())).thenReturn(true);

    MockMvc mockMvc = MockMvcBuilders.standaloneSetup(new DummyActuatorController())
        .addFilters(
            new RequestIdFilter(),
            new JwtAuthFilter(
                properties,
                new JwtAuthService(properties),
                rateLimitStore,
                Mockito.mock(SecurityMonitoringService.class)
            )
        )
        .build();

    mockMvc.perform(get("/actuator/prometheus"))
        .andExpect(status().isUnauthorized())
        .andExpect(jsonPath("$.code").value("AUTH_FAILED"));
  }

  @RestController
  static class DummyActuatorController {
    @GetMapping("/actuator/prometheus")
    Map<String, String> prometheus() {
      return Map.of("status", "ok");
    }
  }
}
