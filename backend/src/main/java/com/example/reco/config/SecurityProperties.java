package com.example.reco.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "api.auth")
public class SecurityProperties {
  private boolean enabled = false;
  private String header = "x-api-key";
  private String value = "";
  private String adminHeader = "x-admin-key";
  private String adminValue = "";

  public boolean isEnabled() {
    return enabled;
  }

  public void setEnabled(boolean enabled) {
    this.enabled = enabled;
  }

  public String getHeader() {
    return header;
  }

  public void setHeader(String header) {
    this.header = header;
  }

  public String getValue() {
    return value;
  }

  public void setValue(String value) {
    this.value = value;
  }

  public String getAdminHeader() {
    return adminHeader;
  }

  public void setAdminHeader(String adminHeader) {
    this.adminHeader = adminHeader;
  }

  public String getAdminValue() {
    return adminValue;
  }

  public void setAdminValue(String adminValue) {
    this.adminValue = adminValue;
  }
}
