package com.example.reco.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.example.reco.service.RateLimitStore;
import jakarta.servlet.ServletException;
import java.io.IOException;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;
import org.springframework.mock.web.MockFilterChain;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

class RateLimitFilterTest {
  @Test
  void returnsStructuredErrorWithRequestId() throws ServletException, IOException {
    RateLimitStore store = mock(RateLimitStore.class);
    when(store.allow("unknown", 60, 60)).thenReturn(false);

    RateLimitProperties properties = new RateLimitProperties();
    properties.setEnabled(true);
    RateLimitFilter filter = new RateLimitFilter(properties, store);
    MockHttpServletResponse response = new MockHttpServletResponse();

    MDC.put("requestId", "req_limit");
    filter.doFilter(new MockHttpServletRequest("GET", "/api/recommendations"), response, new MockFilterChain());
    MDC.remove("requestId");

    assertEquals(429, response.getStatus());
    assertTrue(response.getContentAsString().contains("\"requestId\":\"req_limit\""));
    assertTrue(response.getContentAsString().contains("\"code\":\"RATE_LIMITED\""));
  }
}
