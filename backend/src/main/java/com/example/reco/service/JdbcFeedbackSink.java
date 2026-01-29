package com.example.reco.service;

import com.example.reco.dto.FeedbackRequest;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "feedback.sink", havingValue = "db", matchIfMissing = true)
public class JdbcFeedbackSink implements FeedbackSink {
  private final JdbcTemplate jdbcTemplate;
  private final ObjectMapper objectMapper = new ObjectMapper();

  public JdbcFeedbackSink(JdbcTemplate jdbcTemplate) {
    this.jdbcTemplate = jdbcTemplate;
  }

  @Override
  public void write(FeedbackRequest request) {
    String sql = "insert into feedback_events (request_id, user_id, item_id, event_type, scene, model_version, ts, extra) values (?, ?, ?, ?, ?, ?, ?, ?::jsonb)";
    String extraJson = null;
    if (request.extra() != null) {
      try {
        extraJson = objectMapper.writeValueAsString(request.extra());
      } catch (JsonProcessingException e) {
        throw new RuntimeException("failed to serialize feedback extra", e);
      }
    }
    jdbcTemplate.update(
        sql,
        request.requestId(),
        request.userId(),
        request.itemId(),
        request.eventType(),
        request.scene(),
        request.modelVersion(),
        request.ts(),
        extraJson
    );
  }
}
