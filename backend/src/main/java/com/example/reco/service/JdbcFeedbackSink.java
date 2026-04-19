package com.example.reco.service;

import com.example.reco.config.FeedbackPrivacyProperties;
import com.example.reco.dto.FeedbackRequest;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Map;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "feedback.sink", havingValue = "db")
public class JdbcFeedbackSink implements FeedbackSink {
  private final JdbcTemplate jdbcTemplate;
  private final ObjectMapper objectMapper = new ObjectMapper();
  private final UserTokenService userTokenService;
  private final FeedbackExtraSanitizer extraSanitizer;
  private final FeedbackPrivacyProperties privacyProperties;

  public JdbcFeedbackSink(
      JdbcTemplate jdbcTemplate,
      UserTokenService userTokenService,
      FeedbackExtraSanitizer extraSanitizer,
      FeedbackPrivacyProperties privacyProperties
  ) {
    this.jdbcTemplate = jdbcTemplate;
    this.userTokenService = userTokenService;
    this.extraSanitizer = extraSanitizer;
    this.privacyProperties = privacyProperties;
  }

  @Override
  public void write(FeedbackRequest request) {
    String sql = "insert into feedback_events (request_id, user_id, item_id, event_type, scene, model_version, ts, extra) values (?, ?, ?, ?, ?, ?, ?, ?::jsonb)";
    String userToken = userTokenService.tokenize(request.userId());
    boolean includeOptional = privacyProperties.isCollectOptionalFields();
    String modelVersion = includeOptional ? request.modelVersion() : null;
    String extraJson = buildExtraJson(request.extra(), includeOptional);

    jdbcTemplate.update(
        sql,
        request.requestId(),
        userToken,
        request.itemId(),
        request.eventType(),
        request.scene(),
        modelVersion,
        request.ts(),
        extraJson
    );
  }

  private String buildExtraJson(Map<String, Object> extra, boolean includeOptional) {
    if (!includeOptional || extra == null) {
      return null;
    }
    Map<String, Object> sanitized = extraSanitizer.sanitize(extra);
    if (sanitized.isEmpty()) {
      return null;
    }
    try {
      return objectMapper.writeValueAsString(sanitized);
    } catch (JsonProcessingException e) {
      throw new RuntimeException("failed to serialize feedback extra", e);
    }
  }
}
