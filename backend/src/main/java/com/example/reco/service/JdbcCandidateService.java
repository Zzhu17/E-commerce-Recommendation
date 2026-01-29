package com.example.reco.service;

import java.util.List;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "candidate.source", havingValue = "db", matchIfMissing = true)
public class JdbcCandidateService implements CandidateService {
  private final JdbcTemplate jdbcTemplate;

  public JdbcCandidateService(JdbcTemplate jdbcTemplate) {
    this.jdbcTemplate = jdbcTemplate;
  }

  @Override
  public List<String> getCandidates(String userId, String scene, int limit) {
    String sql = "select item_id from candidates where user_id = ? and scene = ? order by score desc, updated_at desc limit ?";
    return jdbcTemplate.query(sql, (rs, rowNum) -> rs.getString("item_id"), userId, scene, limit);
  }
}
