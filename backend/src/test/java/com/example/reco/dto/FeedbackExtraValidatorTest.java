package com.example.reco.dto;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

class FeedbackExtraValidatorTest {
  private final FeedbackExtraValidator validator = new FeedbackExtraValidator();

  @Test
  void rejectsNestedPayload() {
    Map<String, Object> extra = new HashMap<>();
    extra.put("safe_key", Map.of("nested", "value"));
    assertFalse(validator.isValid(extra, null));
  }

  @Test
  void rejectsOversizedPayload() {
    Map<String, Object> extra = new HashMap<>();
    extra.put("source", "x".repeat(3000));
    assertFalse(validator.isValid(extra, null));
  }

  @Test
  void rejectsInvalidKeyName() {
    Map<String, Object> extra = new HashMap<>();
    extra.put("bad-key", "ok");
    assertFalse(validator.isValid(extra, null));
  }

  @Test
  void acceptsScalarWhitelistedStylePayload() {
    Map<String, Object> extra = new HashMap<>();
    extra.put("source", "search");
    extra.put("position", 2);
    assertTrue(validator.isValid(extra, null));
  }
}
