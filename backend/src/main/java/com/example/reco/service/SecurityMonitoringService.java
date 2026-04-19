package com.example.reco.service;

import com.example.reco.util.SensitiveDataMasker;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.stereotype.Service;

@Service
public class SecurityMonitoringService {
  private final MeterRegistry meterRegistry;

  public SecurityMonitoringService(MeterRegistry meterRegistry) {
    this.meterRegistry = meterRegistry;
  }

  public void recordAuthFailure(String path, String remoteIp) {
    Counter.builder("security_auth_failures_total")
        .tag("path", safe(path))
        .tag("source", SensitiveDataMasker.maskIdentifier(remoteIp))
        .register(meterRegistry)
        .increment();

    Counter.builder("security_failed_login_source_total")
        .tag("source", SensitiveDataMasker.maskIdentifier(remoteIp))
        .register(meterRegistry)
        .increment();
  }

  public void recordForbidden(String path) {
    Counter.builder("security_forbidden_total")
        .tag("path", safe(path))
        .register(meterRegistry)
        .increment();
  }

  public void recordAdminCall(String path, String outcome) {
    Counter.builder("security_admin_calls_total")
        .tag("path", safe(path))
        .tag("outcome", safe(outcome))
        .register(meterRegistry)
        .increment();
  }

  private String safe(String value) {
    return value == null || value.isBlank() ? "unknown" : value;
  }
}
