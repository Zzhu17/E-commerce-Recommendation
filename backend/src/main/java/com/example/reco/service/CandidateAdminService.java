package com.example.reco.service;

import com.example.reco.config.AccessGuardProperties;
import com.example.reco.dto.CandidateRow;
import com.example.reco.dto.CandidateUpsertRequest;
import java.util.List;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class CandidateAdminService {
  private final JdbcTemplate jdbcTemplate;
  private final AccessGuardProperties guardProperties;

  public CandidateAdminService(JdbcTemplate jdbcTemplate, AccessGuardProperties guardProperties) {
    this.jdbcTemplate = jdbcTemplate;
    this.guardProperties = guardProperties;
    this.jdbcTemplate.setQueryTimeout(guardProperties.getDbQueryTimeoutSeconds());
  }

  public int upsert(List<CandidateUpsertRequest> items) {
    int maxBatch = guardProperties.getMaxAdminBatchSize();
    if (items.size() > maxBatch) {
      throw new IllegalArgumentException("batch size exceeds limit");
    }
    String sql = """
        insert into candidates (user_id, scene, item_id, score, updated_at)
        values (?, ?, ?, ?, now())
        on conflict (user_id, scene, item_id)
        do update set score = excluded.score, updated_at = now()
        """;
    int count = 0;
    for (CandidateUpsertRequest item : items) {
      count += jdbcTemplate.update(sql, item.userId(), item.scene(), item.itemId(), item.score());
    }
    return count;
  }

  public List<CandidateRow> list(String userId, String scene, int limit) {
    int safeLimit = Math.min(limit, guardProperties.getMaxAdminListLimit());
    String sql = """
        select item_id, score, updated_at
        from candidates
        where user_id = ? and scene = ?
        order by score desc, updated_at desc
        limit ?
        """;
    return jdbcTemplate.query(
        sql,
        (rs, rowNum) -> new CandidateRow(
            rs.getString("item_id"),
            rs.getDouble("score"),
            rs.getString("updated_at")
        ),
        userId,
        scene,
        safeLimit
    );
  }
}
