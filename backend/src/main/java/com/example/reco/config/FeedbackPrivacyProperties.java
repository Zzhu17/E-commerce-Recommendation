package com.example.reco.config;

import java.util.List;
import java.util.Map;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "privacy.feedback")
public class FeedbackPrivacyProperties {
  private boolean collectOptionalFields;
  private List<String> extraWhitelist;
  private UserToken userToken;

  public boolean isCollectOptionalFields() {
    return collectOptionalFields;
  }

  public void setCollectOptionalFields(boolean collectOptionalFields) {
    this.collectOptionalFields = collectOptionalFields;
  }

  public List<String> getExtraWhitelist() {
    return extraWhitelist;
  }

  public void setExtraWhitelist(List<String> extraWhitelist) {
    this.extraWhitelist = extraWhitelist;
  }

  public UserToken getUserToken() {
    return userToken;
  }

  public void setUserToken(UserToken userToken) {
    this.userToken = userToken;
  }

  public static class UserToken {
    private String activeSaltVersion;
    private String pepper;
    private Map<String, String> salts;

    public String getActiveSaltVersion() {
      return activeSaltVersion;
    }

    public void setActiveSaltVersion(String activeSaltVersion) {
      this.activeSaltVersion = activeSaltVersion;
    }

    public String getPepper() {
      return pepper;
    }

    public void setPepper(String pepper) {
      this.pepper = pepper;
    }

    public Map<String, String> getSalts() {
      return salts;
    }

    public void setSalts(Map<String, String> salts) {
      this.salts = salts;
    }
  }
}
