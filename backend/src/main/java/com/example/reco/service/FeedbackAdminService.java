package com.example.reco.service;

import com.example.reco.dto.FeedbackEvent;
import java.util.List;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class FeedbackAdminService {
  private final JdbcTemplate jdbcTemplate;
  private final UserTokenService userTokenService;

  public FeedbackAdminService(JdbcTemplate jdbcTemplate, UserTokenService userTokenService) {
    this.jdbcTemplate = jdbcTemplate;
    this.userTokenService = userTokenService;
  }

  public List<FeedbackEvent> listByUser(String userId, int limit) {
    String sql = """
        select request_id, user_id, item_id, event_type, scene, model_version, ts, extra, created_at
        from feedback_events
        where user_id = ?
        order by created_at desc
        limit ?
        """;
    return jdbcTemplate.query(
        sql,
        (rs, rowNum) -> new FeedbackEvent(
            rs.getString("request_id"),
            rs.getString("user_id"),
            rs.getString("item_id"),
            rs.getString("event_type"),
            rs.getString("scene"),
            rs.getString("model_version"),
            rs.getLong("ts"),
            rs.getString("extra"),
            rs.getString("created_at")
        ),
        userTokenService.tokenize(userId),
        limit
    );
  }
}
