package com.example.reco.service;

import com.example.reco.config.AccessGuardProperties;
import java.time.Duration;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "api.rate-limit.store", havingValue = "redis")
public class RedisRateLimitStore implements RateLimitStore {
  private final StringRedisTemplate redisTemplate;
  private final AccessGuardProperties guardProperties;
  private final ExecutorService executor;

  public RedisRateLimitStore(StringRedisTemplate redisTemplate, AccessGuardProperties guardProperties) {
    this(redisTemplate, guardProperties, Executors.newCachedThreadPool());
  }

  RedisRateLimitStore(StringRedisTemplate redisTemplate, AccessGuardProperties guardProperties, ExecutorService executor) {
    this.redisTemplate = redisTemplate;
    this.guardProperties = guardProperties;
    this.executor = executor;
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
    }, true);
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

  private <T> T runWithTimeout(Callable<T> action, T fallbackValue) {
    Future<T> future = executor.submit(action);
    try {
      return future.get(guardProperties.getCacheTimeoutMillis(), TimeUnit.MILLISECONDS);
    } catch (TimeoutException ex) {
      future.cancel(true);
      return fallbackValue;
    } catch (InterruptedException ex) {
      Thread.currentThread().interrupt();
      return fallbackValue;
    } catch (ExecutionException ex) {
      return fallbackValue;
    }
  }
}
