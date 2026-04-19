package com.example.reco.service;

import java.time.Instant;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class RetentionAuditService {
  private final JdbcTemplate jdbcTemplate;

  public RetentionAuditService(JdbcTemplate jdbcTemplate) {
    this.jdbcTemplate = jdbcTemplate;
  }

  public void recordRun(
      String jobName,
      String status,
      long affectedRows,
      String details,
      Instant startedAt,
      Instant finishedAt
  ) {
    String sql = """
        insert into retention_job_audit (job_name, started_at, finished_at, status, affected_rows, details)
        values (?, ?, ?, ?, ?, ?)
        """;
    jdbcTemplate.update(sql, jobName, startedAt, finishedAt, status, affectedRows, details);
  }
}
