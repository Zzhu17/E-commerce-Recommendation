package com.example.reco.dto;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.regex.Pattern;

public class FeedbackExtraValidator implements ConstraintValidator<ValidFeedbackExtra, Map<String, Object>> {
  private static final int MAX_BYTES = 2048;
  private static final int MAX_KEYS = 16;
  private static final Pattern KEY_PATTERN = Pattern.compile("^[a-z][a-z0-9_]{0,31}$");

  @Override
  public boolean isValid(Map<String, Object> value, ConstraintValidatorContext context) {
    if (value == null || value.isEmpty()) {
      return true;
    }
    if (value.size() > MAX_KEYS) {
      return false;
    }
    int bytes = 0;
    for (Map.Entry<String, Object> entry : value.entrySet()) {
      String key = entry.getKey();
      if (key == null || !KEY_PATTERN.matcher(key).matches()) {
        return false;
      }
      Object raw = entry.getValue();
      if (!(raw == null || raw instanceof String || raw instanceof Number || raw instanceof Boolean)) {
        return false;
      }
      String piece = key + "=" + String.valueOf(raw);
      bytes += piece.getBytes(StandardCharsets.UTF_8).length;
      if (bytes > MAX_BYTES) {
        return false;
      }
    }
    return true;
  }
}
