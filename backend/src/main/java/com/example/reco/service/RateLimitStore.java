package com.example.reco.service;

public interface RateLimitStore {
  boolean allow(String key, int limit, int windowSeconds);

  void block(String key, int windowSeconds);

  boolean isBlocked(String key);
}
