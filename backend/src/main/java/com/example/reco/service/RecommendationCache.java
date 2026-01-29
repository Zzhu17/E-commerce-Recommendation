package com.example.reco.service;

import com.example.reco.config.RecoCacheProperties;
import com.example.reco.dto.RecommendationResponse;
import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Service;

@Service
public class RecommendationCache {
  private static class CacheEntry {
    private final RecommendationResponse response;
    private final long expiresAt;

    private CacheEntry(RecommendationResponse response, long expiresAt) {
      this.response = response;
      this.expiresAt = expiresAt;
    }
  }

  private final RecoCacheProperties properties;
  private final Map<String, CacheEntry> cache = new ConcurrentHashMap<>();

  public RecommendationCache(RecoCacheProperties properties) {
    this.properties = properties;
  }

  public RecommendationResponse get(String key) {
    if (!properties.isEnabled()) {
      return null;
    }
    CacheEntry entry = cache.get(key);
    if (entry == null) {
      return null;
    }
    if (Instant.now().getEpochSecond() > entry.expiresAt) {
      cache.remove(key);
      return null;
    }
    return entry.response;
  }

  public void put(String key, RecommendationResponse response) {
    if (!properties.isEnabled() || response == null) {
      return;
    }
    long expiresAt = Instant.now().getEpochSecond() + properties.getTtlSeconds();
    cache.put(key, new CacheEntry(response, expiresAt));
  }
}
