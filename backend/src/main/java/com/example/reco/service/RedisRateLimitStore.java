package com.example.reco.service;

import java.time.Duration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "api.rate-limit.store", havingValue = "redis")
public class RedisRateLimitStore implements RateLimitStore {
  private final StringRedisTemplate redisTemplate;

  public RedisRateLimitStore(StringRedisTemplate redisTemplate) {
    this.redisTemplate = redisTemplate;
  }

  @Override
  public boolean allow(String key, int limit, int windowSeconds) {
    String redisKey = "rate:" + key;
    Long count = redisTemplate.opsForValue().increment(redisKey);
    if (count != null && count == 1L) {
      redisTemplate.expire(redisKey, Duration.ofSeconds(windowSeconds));
    }
    return count != null && count <= limit;
  }
}
