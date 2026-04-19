package com.example.reco.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "api.auth")
public class SecurityProperties {
  private boolean enabled = true;
  private String jwtSecret = "";
  private String issuer = "reco-api";
  private String audience = "reco-admin";
  private long clockSkewSeconds = 30;
  private String rolesClaim = "roles";
  private String readOpsRole = "ops_read";
  private String writeOpsRole = "ops_write";
  private String platformAdminRole = "platform_admin";
  private int authFailureLimit = 10;
  private int authFailureWindowSeconds = 60;

  public boolean isEnabled() {
    return enabled;
  }

  public void setEnabled(boolean enabled) {
    this.enabled = enabled;
  }

  public String getJwtSecret() {
    return jwtSecret;
  }

  public void setJwtSecret(String jwtSecret) {
    this.jwtSecret = jwtSecret;
  }

  public String getIssuer() {
    return issuer;
  }

  public void setIssuer(String issuer) {
    this.issuer = issuer;
  }

  public String getAudience() {
    return audience;
  }

  public void setAudience(String audience) {
    this.audience = audience;
  }

  public long getClockSkewSeconds() {
    return clockSkewSeconds;
  }

  public void setClockSkewSeconds(long clockSkewSeconds) {
    this.clockSkewSeconds = clockSkewSeconds;
  }

  public String getRolesClaim() {
    return rolesClaim;
  }

  public void setRolesClaim(String rolesClaim) {
    this.rolesClaim = rolesClaim;
  }

  public String getReadOpsRole() {
    return readOpsRole;
  }

  public void setReadOpsRole(String readOpsRole) {
    this.readOpsRole = readOpsRole;
  }

  public String getWriteOpsRole() {
    return writeOpsRole;
  }

  public void setWriteOpsRole(String writeOpsRole) {
    this.writeOpsRole = writeOpsRole;
  }

  public String getPlatformAdminRole() {
    return platformAdminRole;
  }

  public void setPlatformAdminRole(String platformAdminRole) {
    this.platformAdminRole = platformAdminRole;
  }

  public int getAuthFailureLimit() {
    return authFailureLimit;
  }

  public void setAuthFailureLimit(int authFailureLimit) {
    this.authFailureLimit = authFailureLimit;
  }

  public int getAuthFailureWindowSeconds() {
    return authFailureWindowSeconds;
  }

  public void setAuthFailureWindowSeconds(int authFailureWindowSeconds) {
    this.authFailureWindowSeconds = authFailureWindowSeconds;
  }
}
