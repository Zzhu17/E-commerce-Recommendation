package com.example.reco.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.example.reco.config.AccessGuardProperties;
import com.example.reco.config.FeedbackPrivacyProperties;
import com.example.reco.dto.FeedbackRequest;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.slf4j.MDC;
import org.springframework.jdbc.core.JdbcTemplate;

class FeedbackSinkRequestIdTest {
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  @TempDir Path tempDir;

  @AfterEach
  void clearRequestId() {
    MDC.remove("requestId");
  }

  @Test
  void jdbcSinkPersistsCanonicalRequestId() {
    MDC.put("requestId", "req_header");
    JdbcTemplate jdbcTemplate = mock(JdbcTemplate.class);
    UserTokenService userTokenService = mock(UserTokenService.class);
    when(userTokenService.tokenize("user123")).thenReturn("tok_user");
    FeedbackExtraSanitizer extraSanitizer = mock(FeedbackExtraSanitizer.class);

    JdbcFeedbackSink sink = new JdbcFeedbackSink(
        jdbcTemplate,
        userTokenService,
        extraSanitizer,
        privacyProperties(false),
        new AccessGuardProperties()
    );

    sink.write(request("req_body"));

    verify(jdbcTemplate).setQueryTimeout(anyInt());
    verify(jdbcTemplate).update(
        eq("insert into feedback_events (request_id, user_id, item_id, event_type, scene, model_version, ts, extra) values (?, ?, ?, ?, ?, ?, ?, ?::jsonb)"),
        eq("req_header"),
        eq("tok_user"),
        eq("item001"),
        eq("click"),
        eq("home"),
        eq(null),
        eq(1710000000000L),
        eq(null)
    );
  }

  @Test
  void fileSinkPersistsCanonicalRequestId() throws IOException {
    MDC.put("requestId", "req_header");
    UserTokenService userTokenService = mock(UserTokenService.class);
    when(userTokenService.tokenize("user123")).thenReturn("tok_user");
    FeedbackExtraSanitizer extraSanitizer = mock(FeedbackExtraSanitizer.class);
    Path sinkPath = tempDir.resolve("feedback.jsonl");

    FileFeedbackSink sink = new FileFeedbackSink(
        sinkPath.toString(),
        userTokenService,
        extraSanitizer,
        privacyProperties(false)
    );

    sink.write(request("req_body"));

    Map<String, Object> payload = OBJECT_MAPPER.readValue(
        Files.readString(sinkPath),
        new TypeReference<>() {}
    );
    assertEquals("req_header", payload.get("requestId"));
    assertNotEquals("req_body", payload.get("requestId"));
  }

  private FeedbackPrivacyProperties privacyProperties(boolean collectOptionalFields) {
    FeedbackPrivacyProperties properties = new FeedbackPrivacyProperties();
    properties.setCollectOptionalFields(collectOptionalFields);
    return properties;
  }

  private FeedbackRequest request(String requestId) {
    return new FeedbackRequest(
        requestId,
        "user123",
        "item001",
        "click",
        "home",
        "v1",
        1710000000000L,
        Map.of("trace", "ignored")
    );
  }
}
