package com.example.reco.service;

import com.example.reco.config.ModelProperties;
import com.example.reco.dto.ModelRecommendRequest;
import com.example.reco.dto.ModelRecommendResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class ModelClient {
  private static final Logger log = LoggerFactory.getLogger(ModelClient.class);

  private final RestTemplate restTemplate;
  private final ModelProperties properties;

  public ModelClient(RestTemplate restTemplate, ModelProperties properties) {
    this.restTemplate = restTemplate;
    this.properties = properties;
  }

  public ModelRecommendResponse recommend(ModelRecommendRequest request) {
    long start = System.nanoTime();
    int attempts = 0;
    try {
      while (attempts < 3) {
        attempts++;
        try {
          ResponseEntity<ModelRecommendResponse> response = restTemplate.exchange(
              properties.getBaseUrl() + "/model/recommend",
              HttpMethod.POST,
              new HttpEntity<>(request),
              ModelRecommendResponse.class
          );
          ModelRecommendResponse body = response.getBody();
          if (body == null) {
            log.warn("Model response body is null for requestId={}", request.requestId());
          }
          return body;
        } catch (Exception ex) {
          log.warn("Model call failed (attempt {} of 3) requestId={}: {}",
              attempts, request.requestId(), ex.getMessage());
          if (attempts >= 3) {
            return null;
          }
          try {
            Thread.sleep(100L * attempts);
          } catch (InterruptedException ie) {
            Thread.currentThread().interrupt();
            return null;
          }
        }
      }
      return null;
    } finally {
      long elapsedMs = (System.nanoTime() - start) / 1_000_000;
      log.info("Model call latency {} ms for requestId={}", elapsedMs, request.requestId());
    }
  }
}
