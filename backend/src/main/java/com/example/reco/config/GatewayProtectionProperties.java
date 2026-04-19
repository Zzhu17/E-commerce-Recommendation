package com.example.reco.config;

import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "gateway.protection")
public class GatewayProtectionProperties {
  private boolean enabled = true;
  private int ipRateLimitPerMinute = 120;
  private int userAgentRateLimitPerMinute = 300;
  private int banSeconds = 900;
  private List<String> blockedUserAgents = List.of("sqlmap", "nikto", "nmap", "masscan", "python-requests", "go-http-client");
  private List<String> blockedPathPatterns = List.of("\\.git", "\\.env", "wp-admin", "wp-login", "phpmyadmin", "\\.php", "\\.sql", "\\.bak", "etc/passwd");

  public boolean isEnabled() {
    return enabled;
  }

  public void setEnabled(boolean enabled) {
    this.enabled = enabled;
  }

  public int getIpRateLimitPerMinute() {
    return ipRateLimitPerMinute;
  }

  public void setIpRateLimitPerMinute(int ipRateLimitPerMinute) {
    this.ipRateLimitPerMinute = ipRateLimitPerMinute;
  }

  public int getUserAgentRateLimitPerMinute() {
    return userAgentRateLimitPerMinute;
  }

  public void setUserAgentRateLimitPerMinute(int userAgentRateLimitPerMinute) {
    this.userAgentRateLimitPerMinute = userAgentRateLimitPerMinute;
  }

  public int getBanSeconds() {
    return banSeconds;
  }

  public void setBanSeconds(int banSeconds) {
    this.banSeconds = banSeconds;
  }

  public List<String> getBlockedUserAgents() {
    return blockedUserAgents;
  }

  public void setBlockedUserAgents(List<String> blockedUserAgents) {
    this.blockedUserAgents = blockedUserAgents;
  }

  public List<String> getBlockedPathPatterns() {
    return blockedPathPatterns;
  }

  public void setBlockedPathPatterns(List<String> blockedPathPatterns) {
    this.blockedPathPatterns = blockedPathPatterns;
  }
}
