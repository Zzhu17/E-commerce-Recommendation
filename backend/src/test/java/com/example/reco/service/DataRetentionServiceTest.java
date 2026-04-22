package com.example.reco.service;

import static org.mockito.ArgumentMatchers.contains;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.example.reco.config.DataRetentionProperties;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class DataRetentionServiceTest {
  @TempDir Path tempDir;

  @Test
  void skipsMissingArtifactPaths() {
    DataRetentionProperties properties = new DataRetentionProperties();
    properties.setHotDays(90);
    properties.setWarmDays(180);
    properties.setColdDays(365);

    DataRetentionProperties.Cleanup cleanup = new DataRetentionProperties.Cleanup();
    cleanup.setBatchSize(100);
    properties.setCleanup(cleanup);

    DataRetentionProperties.Artifact artifact = new DataRetentionProperties.Artifact();
    artifact.setTtlDays(30);
    artifact.setIncludeExtensions(List.of(".json"));
    artifact.setPaths(List.of(tempDir.resolve("missing").toString()));
    properties.setArtifact(artifact);

    RetentionAuditService retentionAuditService = mock(RetentionAuditService.class);
    FeedbackAdminService feedbackAdminService = mock(FeedbackAdminService.class);
    when(feedbackAdminService.refreshStorageTier(90, 180, 365)).thenReturn(0);
    when(feedbackAdminService.purgeExpiredFeedback(365, 100)).thenReturn(0);

    DataRetentionService service = new DataRetentionService(properties, retentionAuditService, feedbackAdminService);
    service.runScheduledRetention();

    verify(retentionAuditService).recordRun(
        eq("retention_cleanup"),
        eq("success"),
        eq(0L),
        contains("purged-count=0"),
        org.mockito.ArgumentMatchers.any(),
        org.mockito.ArgumentMatchers.any()
    );
  }

  @Test
  void continuesPurgingWhenOnePathIsMissing() throws IOException {
    Path artifactsDir = tempDir.resolve("artifacts");
    Files.createDirectories(artifactsDir);
    Path expired = artifactsDir.resolve("old.json");
    Files.writeString(expired, "{}");
    Files.setLastModifiedTime(expired, FileTime.fromMillis(System.currentTimeMillis() - 40L * 24 * 3600 * 1000));

    DataRetentionProperties properties = new DataRetentionProperties();
    properties.setHotDays(90);
    properties.setWarmDays(180);
    properties.setColdDays(365);

    DataRetentionProperties.Cleanup cleanup = new DataRetentionProperties.Cleanup();
    cleanup.setBatchSize(100);
    properties.setCleanup(cleanup);

    DataRetentionProperties.Artifact artifact = new DataRetentionProperties.Artifact();
    artifact.setTtlDays(30);
    artifact.setIncludeExtensions(List.of(".json"));
    artifact.setPaths(List.of(tempDir.resolve("missing").toString(), artifactsDir.toString()));
    properties.setArtifact(artifact);

    RetentionAuditService retentionAuditService = mock(RetentionAuditService.class);
    FeedbackAdminService feedbackAdminService = mock(FeedbackAdminService.class);
    when(feedbackAdminService.refreshStorageTier(90, 180, 365)).thenReturn(0);
    when(feedbackAdminService.purgeExpiredFeedback(365, 100)).thenReturn(0);

    DataRetentionService service = new DataRetentionService(properties, retentionAuditService, feedbackAdminService);
    service.runScheduledRetention();

    verify(retentionAuditService).recordRun(
        eq("retention_cleanup"),
        eq("success"),
        eq(1L),
        contains("skipped-paths=" + tempDir.resolve("missing")),
        org.mockito.ArgumentMatchers.any(),
        org.mockito.ArgumentMatchers.any()
    );
  }
}
