package com.example.reco.config;

import com.example.reco.util.RequestIdUtil;
import com.example.reco.util.SensitiveDataMasker;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.filter.OncePerRequestFilter;

public class StructuredAccessLogFilter extends OncePerRequestFilter {
  private static final Logger log = LoggerFactory.getLogger(StructuredAccessLogFilter.class);

  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
      throws ServletException, IOException {
    long start = System.nanoTime();
    try {
      filterChain.doFilter(request, response);
    } finally {
      long latencyMs = (System.nanoTime() - start) / 1_000_000;
      log.info("event=api_access requestId={} method={} path={} status={} latencyMs={} userId={} itemId={} requestBody={} clientIp={} userAgent={}",
          RequestIdUtil.currentOrUnknown(),
          request.getMethod(),
          safe(request.getRequestURI()),
          response.getStatus(),
          latencyMs,
          SensitiveDataMasker.maskIdentifier(request.getParameter("userId")),
          SensitiveDataMasker.maskIdentifier(request.getParameter("itemId")),
          SensitiveDataMasker.redactedBody(),
          SensitiveDataMasker.maskIdentifier(request.getRemoteAddr()),
          safe(request.getHeader("User-Agent"))
      );
    }
  }

  private String safe(String value) {
    return value == null ? "unknown" : value;
  }
}
