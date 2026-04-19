package com.example.reco.service;

import com.example.reco.config.FeedbackPrivacyProperties;
import com.example.reco.dto.FeedbackRequest;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "feedback.sink", havingValue = "file")
public class FileFeedbackSink implements FeedbackSink {
  private final Path sinkPath;
  private final ObjectMapper objectMapper = new ObjectMapper();
  private final UserTokenService userTokenService;
  private final FeedbackExtraSanitizer extraSanitizer;
  private final FeedbackPrivacyProperties privacyProperties;

  public FileFeedbackSink(
      @Value("${feedback.sink-path}") String sinkPath,
      UserTokenService userTokenService,
      FeedbackExtraSanitizer extraSanitizer,
      FeedbackPrivacyProperties privacyProperties
  ) {
    this.sinkPath = Path.of(sinkPath);
    this.userTokenService = userTokenService;
    this.extraSanitizer = extraSanitizer;
    this.privacyProperties = privacyProperties;
  }

  @Override
  public void write(FeedbackRequest request) {
    try {
      Files.createDirectories(sinkPath.getParent());
      String line = objectMapper.writeValueAsString(sanitizePayload(request)) + System.lineSeparator();
      Files.writeString(sinkPath, line, StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    } catch (JsonProcessingException e) {
      throw new RuntimeException("failed to serialize feedback", e);
    } catch (IOException e) {
      throw new RuntimeException("failed to persist feedback", e);
    }
  }

  private Map<String, Object> sanitizePayload(FeedbackRequest request) {
    Map<String, Object> payload = new LinkedHashMap<>();
    payload.put("requestId", request.requestId());
    payload.put("userId", userTokenService.tokenize(request.userId()));
    payload.put("itemId", request.itemId());
    payload.put("eventType", request.eventType());
    payload.put("scene", request.scene());
    payload.put("ts", request.ts());

    boolean includeOptional = privacyProperties.isCollectOptionalFields();
    if (includeOptional) {
      if (request.modelVersion() != null && !request.modelVersion().isBlank()) {
        payload.put("modelVersion", request.modelVersion());
      }
      Map<String, Object> extra = extraSanitizer.sanitize(request.extra());
      if (!extra.isEmpty()) {
        payload.put("extra", extra);
      }
    }
    return payload;
  }
}
