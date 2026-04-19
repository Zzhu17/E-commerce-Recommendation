package com.example.reco.service;

import com.example.reco.config.DataRetentionProperties;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.List;
import java.util.Locale;
import java.util.stream.Stream;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

@Service
public class DataRetentionService {
  private final DataRetentionProperties properties;
  private final RetentionAuditService retentionAuditService;
  private final FeedbackAdminService feedbackAdminService;

  public DataRetentionService(
      DataRetentionProperties properties,
      RetentionAuditService retentionAuditService,
      FeedbackAdminService feedbackAdminService
  ) {
    this.properties = properties;
    this.retentionAuditService = retentionAuditService;
    this.feedbackAdminService = feedbackAdminService;
  }

  @Scheduled(cron = "${retention.cleanup.cron}")
  public void runScheduledRetention() {
    Instant startedAt = Instant.now();
    try {
      int tierUpdated = feedbackAdminService.refreshStorageTier(
          properties.getHotDays(),
          properties.getWarmDays(),
          properties.getColdDays()
      );
      int feedbackPurged = feedbackAdminService.purgeExpiredFeedback(
          properties.getColdDays(),
          properties.getCleanup().getBatchSize()
      );
      long artifactsPurged = cleanupArtifacts();
      retentionAuditService.recordRun(
          "retention_cleanup",
          "success",
          tierUpdated + feedbackPurged + artifactsPurged,
          "tier-updated=" + tierUpdated + ",feedback-purged=" + feedbackPurged + ",artifacts-purged=" + artifactsPurged,
          startedAt,
          Instant.now()
      );
    } catch (RuntimeException ex) {
      retentionAuditService.recordRun("retention_cleanup", "failed", 0, ex.getMessage(), startedAt, Instant.now());
      throw ex;
    }
  }

  private long cleanupArtifacts() {
    Instant threshold = Instant.now().minusSeconds((long) properties.getArtifact().getTtlDays() * 24 * 3600);
    List<String> extensions = properties.getArtifact().getIncludeExtensions().stream()
        .map(ext -> ext.toLowerCase(Locale.ROOT))
        .toList();

    long removed = 0;
    for (String configuredPath : properties.getArtifact().getPaths()) {
      try (Stream<Path> stream = Files.walk(Path.of(configuredPath))) {
        removed += stream
            .filter(Files::isRegularFile)
            .mapToLong(path -> deleteIfExpired(path, threshold, extensions))
            .sum();
      } catch (IOException e) {
        throw new IllegalStateException("failed to scan artifact path: " + configuredPath, e);
      }
    }
    return removed;
  }

  private long deleteIfExpired(Path path, Instant threshold, List<String> extensions) {
    String name = path.getFileName().toString().toLowerCase(Locale.ROOT);
    boolean matched = extensions.stream().anyMatch(name::endsWith);
    if (!matched) {
      return 0;
    }

    try {
      if (Files.getLastModifiedTime(path).toInstant().isBefore(threshold) && Files.deleteIfExists(path)) {
        return 1;
      }
      return 0;
    } catch (IOException e) {
      throw new IllegalStateException("failed to delete artifact: " + path, e);
    }
  }
}
