package com.example.reco.controller;

import com.example.reco.dto.ErrorResponse;
import com.example.reco.util.RequestIdUtil;
import jakarta.validation.ConstraintViolationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

@RestControllerAdvice
public class ApiExceptionHandler {
  private static final Logger log = LoggerFactory.getLogger(ApiExceptionHandler.class);

  @ExceptionHandler({MethodArgumentNotValidException.class, ConstraintViolationException.class})
  public ResponseEntity<ErrorResponse> handleValidation(Exception ex) {
    log.warn("Validation error: {}", ex.getClass().getSimpleName());
    ErrorResponse body = new ErrorResponse(RequestIdUtil.currentOrUnknown(), "PARAM_INVALID", "invalid request");
    return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(body);
  }

  @ExceptionHandler(IllegalArgumentException.class)
  public ResponseEntity<ErrorResponse> handleIllegalArgument(IllegalArgumentException ex) {
    log.warn("Illegal argument: {}", ex.getMessage());
    ErrorResponse body = new ErrorResponse(RequestIdUtil.currentOrUnknown(), "PARAM_INVALID", "invalid request");
    return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(body);
  }

  @ExceptionHandler(ResponseStatusException.class)
  public ResponseEntity<ErrorResponse> handleStatus(ResponseStatusException ex) {
    HttpStatus status = HttpStatus.valueOf(ex.getStatusCode().value());
    String code = switch (status) {
      case FORBIDDEN -> "AUTH_FORBIDDEN";
      case UNAUTHORIZED -> "AUTH_FAILED";
      case TOO_MANY_REQUESTS -> "RATE_LIMITED";
      default -> "REQUEST_REJECTED";
    };
    String message = switch (status) {
      case FORBIDDEN -> "forbidden";
      case UNAUTHORIZED -> "authentication failed";
      case TOO_MANY_REQUESTS -> "too many requests";
      default -> "request rejected";
    };
    ErrorResponse body = new ErrorResponse(RequestIdUtil.currentOrUnknown(), code, message);
    return ResponseEntity.status(status).body(body);
  }

  @ExceptionHandler(Exception.class)
  public ResponseEntity<ErrorResponse> handleGeneric(Exception ex) {
    log.error("Unhandled error: {}", ex.getClass().getSimpleName());
    ErrorResponse body = new ErrorResponse(RequestIdUtil.currentOrUnknown(), "INTERNAL_ERROR", "unexpected error");
    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(body);
  }
}
