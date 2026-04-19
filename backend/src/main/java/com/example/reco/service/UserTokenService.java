package com.example.reco.service;

import com.example.reco.config.FeedbackPrivacyProperties;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Map;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.springframework.stereotype.Service;

@Service
public class UserTokenService {
  private final FeedbackPrivacyProperties privacyProperties;

  public UserTokenService(FeedbackPrivacyProperties privacyProperties) {
    this.privacyProperties = privacyProperties;
  }

  public String tokenize(String userId) {
    FeedbackPrivacyProperties.UserToken userToken = requireUserTokenConfig();
    String saltVersion = requireText(userToken.getActiveSaltVersion(), "privacy.feedback.user-token.active-salt-version");
    String pepper = requireText(userToken.getPepper(), "privacy.feedback.user-token.pepper");
    Map<String, String> salts = userToken.getSalts();
    if (salts == null || salts.isEmpty()) {
      throw new IllegalStateException("privacy.feedback.user-token.salts must be configured");
    }
    String salt = requireText(salts.get(saltVersion), "privacy.feedback.user-token.salts." + saltVersion);

    String secret = pepper + ":" + salt;
    String payload = saltVersion + ":" + userId;
    try {
      Mac mac = Mac.getInstance("HmacSHA256");
      mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
      byte[] digest = mac.doFinal(payload.getBytes(StandardCharsets.UTF_8));
      return "tok_" + saltVersion + "_" + Base64.getUrlEncoder().withoutPadding().encodeToString(digest);
    } catch (Exception ex) {
      throw new IllegalStateException("failed to tokenize user id", ex);
    }
  }

  private FeedbackPrivacyProperties.UserToken requireUserTokenConfig() {
    FeedbackPrivacyProperties.UserToken userToken = privacyProperties.getUserToken();
    if (userToken == null) {
      throw new IllegalStateException("privacy.feedback.user-token must be configured");
    }
    return userToken;
  }

  private String requireText(String value, String key) {
    if (value == null || value.isBlank()) {
      throw new IllegalStateException(key + " must be configured");
    }
    return value;
  }
}
