package com.example.reco.service;

import com.example.reco.config.AuthContext;
import com.example.reco.config.SecurityProperties;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Base64;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.springframework.stereotype.Service;

@Service
public class JwtAuthService {
  private static final ObjectMapper MAPPER = new ObjectMapper();
  private static final TypeReference<Map<String, Object>> MAP_TYPE = new TypeReference<>() {
  };
  private final SecurityProperties properties;

  public JwtAuthService(SecurityProperties properties) {
    this.properties = properties;
  }

  public AuthContext verifyBearerToken(String authHeader) {
    if (authHeader == null || !authHeader.startsWith("Bearer ")) {
      return null;
    }
    String token = authHeader.substring("Bearer ".length()).trim();
    if (token.isBlank()) {
      return null;
    }
    return verifyToken(token);
  }

  private AuthContext verifyToken(String token) {
    if (properties.getJwtSecret() == null || properties.getJwtSecret().isBlank()) {
      return null;
    }
    String[] parts = token.split("\\.");
    if (parts.length != 3) {
      return null;
    }
    try {
      String headerPayload = parts[0] + "." + parts[1];
      String expectedSig = sign(headerPayload, properties.getJwtSecret());
      if (!constantTimeEquals(expectedSig, parts[2])) {
        return null;
      }

      Map<String, Object> claims = MAPPER.readValue(base64UrlDecode(parts[1]), MAP_TYPE);
      if (!"HS256".equalsIgnoreCase(readString(parseJson(parts[0]), "alg"))) {
        return null;
      }
      if (!checkTime(claims)) {
        return null;
      }
      if (!properties.getIssuer().equals(readString(claims, "iss"))) {
        return null;
      }
      if (!checkAudience(claims.get("aud"))) {
        return null;
      }

      String subject = readString(claims, "sub");
      if (subject == null || subject.isBlank()) {
        return null;
      }
      return new AuthContext(subject, readRoles(claims));
    } catch (Exception ex) {
      return null;
    }
  }

  private boolean checkTime(Map<String, Object> claims) {
    long now = Instant.now().getEpochSecond();
    long skew = properties.getClockSkewSeconds();
    Long exp = readLong(claims, "exp");
    if (exp == null || exp + skew < now) {
      return false;
    }
    Long nbf = readLong(claims, "nbf");
    if (nbf != null && nbf - skew > now) {
      return false;
    }
    return true;
  }

  private boolean checkAudience(Object audClaim) {
    String expected = properties.getAudience();
    if (audClaim instanceof String aud) {
      return expected.equals(aud);
    }
    if (audClaim instanceof List<?> audList) {
      return audList.stream().map(String::valueOf).anyMatch(expected::equals);
    }
    return false;
  }

  private Set<String> readRoles(Map<String, Object> claims) {
    Object claim = claims.get(properties.getRolesClaim());
    if (claim instanceof String role) {
      return Set.of(role);
    }
    if (claim instanceof List<?> roles) {
      Set<String> set = new LinkedHashSet<>();
      for (Object role : roles) {
        set.add(String.valueOf(role));
      }
      return set;
    }
    return Collections.emptySet();
  }

  private String sign(String data, String secret) throws Exception {
    Mac mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
    return Base64.getUrlEncoder().withoutPadding().encodeToString(mac.doFinal(data.getBytes(StandardCharsets.UTF_8)));
  }

  private boolean constantTimeEquals(String a, String b) {
    if (a.length() != b.length()) {
      return false;
    }
    int result = 0;
    for (int i = 0; i < a.length(); i++) {
      result |= a.charAt(i) ^ b.charAt(i);
    }
    return result == 0;
  }

  private byte[] base64UrlDecode(String value) {
    return Base64.getUrlDecoder().decode(value);
  }

  private Map<String, Object> parseJson(String encoded) throws Exception {
    return MAPPER.readValue(base64UrlDecode(encoded), MAP_TYPE);
  }

  private String readString(Map<String, Object> map, String key) {
    Object value = map.get(key);
    return value == null ? null : String.valueOf(value);
  }

  private Long readLong(Map<String, Object> map, String key) {
    Object value = map.get(key);
    if (value instanceof Number number) {
      return number.longValue();
    }
    if (value instanceof String str && !str.isBlank()) {
      return Long.parseLong(str);
    }
    return null;
  }
}
