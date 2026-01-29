package com.example.reco.config;

import java.time.Duration;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class ModelClientConfig {
  @Bean
  public RestTemplate restTemplate(RestTemplateBuilder builder, ModelProperties properties) {
    return builder
        .setConnectTimeout(Duration.ofMillis(properties.getTimeoutMs()))
        .setReadTimeout(Duration.ofMillis(properties.getTimeoutMs()))
        .build();
  }
}
