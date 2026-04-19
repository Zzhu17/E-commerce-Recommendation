package com.example.reco.config;

import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "retention")
public class DataRetentionProperties {
  private int hotDays;
  private int warmDays;
  private int coldDays;
  private Cleanup cleanup;
  private Artifact artifact;

  public int getHotDays() {
    return hotDays;
  }

  public void setHotDays(int hotDays) {
    this.hotDays = hotDays;
  }

  public int getWarmDays() {
    return warmDays;
  }

  public void setWarmDays(int warmDays) {
    this.warmDays = warmDays;
  }

  public int getColdDays() {
    return coldDays;
  }

  public void setColdDays(int coldDays) {
    this.coldDays = coldDays;
  }

  public Cleanup getCleanup() {
    return cleanup;
  }

  public void setCleanup(Cleanup cleanup) {
    this.cleanup = cleanup;
  }

  public Artifact getArtifact() {
    return artifact;
  }

  public void setArtifact(Artifact artifact) {
    this.artifact = artifact;
  }

  public static class Cleanup {
    private String cron;
    private int batchSize;

    public String getCron() {
      return cron;
    }

    public void setCron(String cron) {
      this.cron = cron;
    }

    public int getBatchSize() {
      return batchSize;
    }

    public void setBatchSize(int batchSize) {
      this.batchSize = batchSize;
    }
  }

  public static class Artifact {
    private int ttlDays;
    private List<String> paths;
    private List<String> includeExtensions;

    public int getTtlDays() {
      return ttlDays;
    }

    public void setTtlDays(int ttlDays) {
      this.ttlDays = ttlDays;
    }

    public List<String> getPaths() {
      return paths;
    }

    public void setPaths(List<String> paths) {
      this.paths = paths;
    }

    public List<String> getIncludeExtensions() {
      return includeExtensions;
    }

    public void setIncludeExtensions(List<String> includeExtensions) {
      this.includeExtensions = includeExtensions;
    }
  }
}
