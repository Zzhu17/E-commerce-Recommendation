package com.example.reco.util;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public final class SensitiveDataMasker {
  private SensitiveDataMasker() {}

  public static String maskIdentifier(String raw) {
    if (raw == null || raw.isBlank()) {
      return "redacted";
    }
    return "h:" + shortSha256(raw.trim());
  }

  public static String redactedBody() {
    return "[REDACTED]";
  }

  private static String shortSha256(String input) {
    try {
      MessageDigest digest = MessageDigest.getInstance("SHA-256");
      byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < 6; i++) {
        sb.append(String.format("%02x", hash[i]));
      }
      return sb.toString();
    } catch (NoSuchAlgorithmException e) {
      throw new IllegalStateException("SHA-256 is required", e);
    }
  }
}
