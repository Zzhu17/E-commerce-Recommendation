package com.example.reco.service;

import com.example.reco.config.AccessGuardProperties;
import java.util.List;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "candidate.source", havingValue = "db", matchIfMissing = true)
public class JdbcCandidateService implements CandidateService {
  private final JdbcTemplate jdbcTemplate;
  private final AccessGuardProperties guardProperties;

  public JdbcCandidateService(JdbcTemplate jdbcTemplate, AccessGuardProperties guardProperties) {
    this.jdbcTemplate = jdbcTemplate;
    this.guardProperties = guardProperties;
    this.jdbcTemplate.setQueryTimeout(guardProperties.getDbQueryTimeoutSeconds());
  }

  @Override
  public List<String> getCandidates(String userId, String scene, int limit) {
    int safeLimit = Math.min(limit, guardProperties.getMaxCandidateFetch());
    String sql = "select item_id from candidates where user_id = ? and scene = ? order by score desc, updated_at desc limit ?";
    return jdbcTemplate.query(sql, (rs, rowNum) -> rs.getString("item_id"), userId, scene, safeLimit);
  }
}
