package com.example.reco.config;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.servlet.ServletException;
import java.io.IOException;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockFilterChain;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

class RequestIdFilterTest {
  @Test
  void replacesForgedRequestId() throws ServletException, IOException {
    RequestIdFilter filter = new RequestIdFilter();
    MockHttpServletRequest request = new MockHttpServletRequest();
    request.addHeader(RequestIdFilter.HEADER, "<script>alert(1)</script>");
    MockHttpServletResponse response = new MockHttpServletResponse();

    filter.doFilter(request, response, new MockFilterChain());

    String returned = response.getHeader(RequestIdFilter.HEADER);
    assertFalse("<script>alert(1)</script>".equals(returned));
    assertTrue(returned.startsWith("req_"));
  }

  @Test
  void usesRequestIdQueryParamWhenHeaderMissing() throws ServletException, IOException {
    RequestIdFilter filter = new RequestIdFilter();
    MockHttpServletRequest request = new MockHttpServletRequest();
    request.setParameter("requestId", "req_from_query");
    MockHttpServletResponse response = new MockHttpServletResponse();

    filter.doFilter(request, response, new MockFilterChain());

    assertEquals("req_from_query", response.getHeader(RequestIdFilter.HEADER));
  }
}
