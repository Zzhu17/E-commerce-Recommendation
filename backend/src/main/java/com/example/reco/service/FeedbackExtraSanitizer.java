package com.example.reco.service;

import com.example.reco.config.FeedbackPrivacyProperties;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.springframework.stereotype.Service;

@Service
public class FeedbackExtraSanitizer {
  private final Set<String> whitelist;

  public FeedbackExtraSanitizer(FeedbackPrivacyProperties privacyProperties) {
    List<String> configured = privacyProperties.getExtraWhitelist();
    if (configured == null || configured.isEmpty()) {
      throw new IllegalStateException("privacy.feedback.extra-whitelist must be configured");
    }
    this.whitelist = new HashSet<>(configured);
  }

  public Map<String, Object> sanitize(Map<String, Object> extra) {
    if (extra == null || extra.isEmpty()) {
      return Collections.emptyMap();
    }
    Map<String, Object> sanitized = new LinkedHashMap<>();
    extra.forEach((key, value) -> {
      if (whitelist.contains(key) && isScalar(value)) {
        sanitized.put(key, value);
      }
    });
    return sanitized;
  }

  private boolean isScalar(Object value) {
    return value == null || value instanceof String || value instanceof Number || value instanceof Boolean;
  }
}
