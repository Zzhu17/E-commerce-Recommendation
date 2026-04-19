package com.example.reco.service;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class AdminAuditService {
  private final JdbcTemplate jdbcTemplate;

  public AdminAuditService(JdbcTemplate jdbcTemplate) {
    this.jdbcTemplate = jdbcTemplate;
  }

  public void log(String actor, String action, String details) {
    String sql = """
        insert into admin_action_audit (actor, action, details)
        values (?, ?, ?)
        """;
    jdbcTemplate.update(sql, actor, action, details);
  }
}
