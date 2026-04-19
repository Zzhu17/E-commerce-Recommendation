package com.example.reco.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "access.guard")
public class AccessGuardProperties {
  private int dbQueryTimeoutSeconds = 2;
  private int maxCandidateFetch = 200;
  private int maxAdminListLimit = 200;
  private int maxAdminBatchSize = 200;
  private long cacheTimeoutMillis = 150;

  public int getDbQueryTimeoutSeconds() {
    return dbQueryTimeoutSeconds;
  }

  public void setDbQueryTimeoutSeconds(int dbQueryTimeoutSeconds) {
    this.dbQueryTimeoutSeconds = dbQueryTimeoutSeconds;
  }

  public int getMaxCandidateFetch() {
    return maxCandidateFetch;
  }

  public void setMaxCandidateFetch(int maxCandidateFetch) {
    this.maxCandidateFetch = maxCandidateFetch;
  }

  public int getMaxAdminListLimit() {
    return maxAdminListLimit;
  }

  public void setMaxAdminListLimit(int maxAdminListLimit) {
    this.maxAdminListLimit = maxAdminListLimit;
  }

  public int getMaxAdminBatchSize() {
    return maxAdminBatchSize;
  }

  public void setMaxAdminBatchSize(int maxAdminBatchSize) {
    this.maxAdminBatchSize = maxAdminBatchSize;
  }

  public long getCacheTimeoutMillis() {
    return cacheTimeoutMillis;
  }

  public void setCacheTimeoutMillis(long cacheTimeoutMillis) {
    this.cacheTimeoutMillis = cacheTimeoutMillis;
  }
}
