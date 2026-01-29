package com.example.reco.service;

public interface RateLimitStore {
  boolean allow(String key, int limit, int windowSeconds);
}
