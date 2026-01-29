package com.example.reco.service;

import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "api.rate-limit.store", havingValue = "memory", matchIfMissing = true)
public class InMemoryRateLimitStore implements RateLimitStore {
  private static class Counter {
    private long windowStart;
    private int count;
  }

  private final Map<String, Counter> counters = new ConcurrentHashMap<>();

  @Override
  public boolean allow(String key, int limit, int windowSeconds) {
    long now = Instant.now().getEpochSecond();
    Counter counter = counters.computeIfAbsent(key, k -> new Counter());
    synchronized (counter) {
      if (now - counter.windowStart >= windowSeconds) {
        counter.windowStart = now;
        counter.count = 0;
      }
      counter.count += 1;
      return counter.count <= limit;
    }
  }
}
