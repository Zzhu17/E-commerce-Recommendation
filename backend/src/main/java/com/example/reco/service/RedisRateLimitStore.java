package com.example.reco.service;

import com.example.reco.config.AccessGuardProperties;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "api.rate-limit.store", havingValue = "redis")
public class RedisRateLimitStore implements RateLimitStore {
  private final StringRedisTemplate redisTemplate;
  private final AccessGuardProperties guardProperties;

  public RedisRateLimitStore(StringRedisTemplate redisTemplate, AccessGuardProperties guardProperties) {
    this.redisTemplate = redisTemplate;
    this.guardProperties = guardProperties;
  }

  @Override
  public boolean allow(String key, int limit, int windowSeconds) {
    return runWithTimeout(() -> {
      String redisKey = "rate:" + key;
      Long count = redisTemplate.opsForValue().increment(redisKey);
      if (count != null && count == 1L) {
        redisTemplate.expire(redisKey, Duration.ofSeconds(windowSeconds));
      }
      return count != null && count <= limit;
    }, false);
  }

  @Override
  public void block(String key, int windowSeconds) {
    runWithTimeout(() -> {
      redisTemplate.opsForValue().set("ban:" + key, "1", Duration.ofSeconds(windowSeconds));
      return null;
    }, null);
  }

  @Override
  public boolean isBlocked(String key) {
    Boolean exists = runWithTimeout(() -> redisTemplate.hasKey("ban:" + key), Boolean.FALSE);
    return Boolean.TRUE.equals(exists);
  }

  private <T> T runWithTimeout(java.util.concurrent.Callable<T> action, T fallback) {
    try {
      return CompletableFuture
          .supplyAsync(() -> {
            try {
              return action.call();
            } catch (Exception e) {
              throw new RuntimeException(e);
            }
          })
          .get(guardProperties.getCacheTimeoutMillis(), TimeUnit.MILLISECONDS);
    } catch (Exception ex) {
      return fallback;
    }
  }
}
