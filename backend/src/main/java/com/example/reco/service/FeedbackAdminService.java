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

  public int deleteByUserToken(String userToken, String reason) {
    String sql = "delete from feedback_events where user_id = ?";
    int deleted = jdbcTemplate.update(sql, userToken);

    String auditSql = """
        insert into user_deletion_audit (user_token, reason, deleted_rows)
        values (?, ?, ?)
        """;
    jdbcTemplate.update(auditSql, userToken, reason, deleted);
    return deleted;
  }

  public int refreshStorageTier(int hotDays, int warmDays, int coldDays) {
    String sql = """
        update feedback_events
        set storage_tier = case
          when created_at >= now() - make_interval(days => ?) then 'hot'
          when created_at >= now() - make_interval(days => ?) then 'warm'
          when created_at >= now() - make_interval(days => ?) then 'cold'
          else 'expired'
        end
        """;
    return jdbcTemplate.update(sql, hotDays, warmDays, coldDays);
  }

  public int purgeExpiredFeedback(int coldDays, int batchSize) {
    int total = 0;
    while (true) {
      String sql = """
          with doomed as (
            select id
            from feedback_events
            where created_at < now() - make_interval(days => ?)
            limit ?
          )
          delete from feedback_events f
          using doomed d
          where f.id = d.id
          """;
      int deleted = jdbcTemplate.update(sql, coldDays, batchSize);
      total += deleted;
      if (deleted < batchSize) {
        return total;
      }
    }
  }
}
