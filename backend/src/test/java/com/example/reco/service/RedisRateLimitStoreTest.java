package com.example.reco.service;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.example.reco.config.AccessGuardProperties;
import java.util.concurrent.AbstractExecutorService;
import java.util.concurrent.Callable;
import java.util.concurrent.Future;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

class RedisRateLimitStoreTest {
  @Test
  void allowShouldFailOpenOnTimeout() {
    StringRedisTemplate redisTemplate = mock(StringRedisTemplate.class);
    AccessGuardProperties properties = new AccessGuardProperties();
    properties.setCacheTimeoutMillis(10);

    RedisRateLimitStore store = new RedisRateLimitStore(redisTemplate, properties, new NeverCompleteExecutor());
    assertTrue(store.allow("k", 10, 60));
  }

  @Test
  void isBlockedShouldReturnFalseOnTimeout() {
    StringRedisTemplate redisTemplate = mock(StringRedisTemplate.class);
    AccessGuardProperties properties = new AccessGuardProperties();
    properties.setCacheTimeoutMillis(10);

    RedisRateLimitStore store = new RedisRateLimitStore(redisTemplate, properties, new NeverCompleteExecutor());
    assertFalse(store.isBlocked("k"));
  }

  @Test
  void blockShouldNotThrowWhenTimeout() {
    StringRedisTemplate redisTemplate = mock(StringRedisTemplate.class);
    ValueOperations<String, String> ops = mock(ValueOperations.class);
    when(redisTemplate.opsForValue()).thenReturn(ops);
    AccessGuardProperties properties = new AccessGuardProperties();
    properties.setCacheTimeoutMillis(10);

    RedisRateLimitStore store = new RedisRateLimitStore(redisTemplate, properties, new NeverCompleteExecutor());
    assertDoesNotThrow(() -> store.block("k", 60));
  }

  private static final class NeverCompleteExecutor extends AbstractExecutorService {
    @Override
    public void shutdown() {}

    @Override
    public java.util.List<Runnable> shutdownNow() {
      return java.util.Collections.emptyList();
    }

    @Override
    public boolean isShutdown() {
      return false;
    }

    @Override
    public boolean isTerminated() {
      return false;
    }

    @Override
    public boolean awaitTermination(long timeout, TimeUnit unit) {
      return false;
    }

    @Override
    public void execute(Runnable command) {
      // no-op
    }

    @Override
    public <T> Future<T> submit(Callable<T> task) {
      FutureTask<T> future = new FutureTask<>(task);
      return new Future<T>() {
        @Override
        public boolean cancel(boolean mayInterruptIfRunning) {
          return future.cancel(mayInterruptIfRunning);
        }

        @Override
        public boolean isCancelled() {
          return future.isCancelled();
        }

        @Override
        public boolean isDone() {
          return false;
        }

        @Override
        public T get() throws InterruptedException {
          Thread.sleep(Long.MAX_VALUE);
          return null;
        }

        @Override
        public T get(long timeout, TimeUnit unit) throws java.util.concurrent.TimeoutException {
          throw new java.util.concurrent.TimeoutException("forced timeout");
        }
      };
    }
  }
}
