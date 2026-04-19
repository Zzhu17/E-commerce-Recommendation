package com.example.reco.config;

import java.time.Duration;
import java.util.List;
import com.example.reco.util.RequestIdUtil;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class ModelClientConfig {
  @Bean
  public RestTemplate restTemplate(RestTemplateBuilder builder, ModelProperties properties) {
    ClientHttpRequestInterceptor requestIdInterceptor = (request, body, execution) -> {
      String requestId = RequestIdUtil.currentOrUnknown();
      request.getHeaders().set(RequestIdFilter.HEADER, requestId);
      return execution.execute(request, body);
    };
    return builder
        .setConnectTimeout(Duration.ofMillis(properties.getTimeoutMs()))
        .setReadTimeout(Duration.ofMillis(properties.getTimeoutMs()))
        .additionalInterceptors(List.of(requestIdInterceptor))
        .build();
  }
}
