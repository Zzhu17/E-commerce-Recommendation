package com.example.reco.config;

import com.example.reco.dto.ErrorResponse;
import com.example.reco.util.RequestIdUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.springframework.http.HttpStatus;

final class FilterErrorResponseWriter {
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  private FilterErrorResponseWriter() {}

  static void write(HttpServletResponse response, HttpStatus status, String code, String message) throws IOException {
    response.setStatus(status.value());
    response.setContentType("application/json");
    response.getWriter().write(OBJECT_MAPPER.writeValueAsString(
        new ErrorResponse(RequestIdUtil.currentOrUnknown(), code, message)
    ));
  }
}
