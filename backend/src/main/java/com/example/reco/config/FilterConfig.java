package com.example.reco.config;

import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class FilterConfig {
  @Bean
  public FilterRegistrationBean<RequestIdFilter> requestIdFilter() {
    FilterRegistrationBean<RequestIdFilter> bean = new FilterRegistrationBean<>();
    bean.setFilter(new RequestIdFilter());
    bean.addUrlPatterns("/*");
    bean.setOrder(0);
    return bean;
  }

  @Bean
  public FilterRegistrationBean<ApiKeyFilter> apiKeyFilter(SecurityProperties securityProperties) {
    ApiKeyFilter filter = new ApiKeyFilter(securityProperties);
    FilterRegistrationBean<ApiKeyFilter> bean = new FilterRegistrationBean<>();
    bean.setFilter(filter);
    bean.addUrlPatterns("/api/*");
    bean.setOrder(1);
    return bean;
  }

  @Bean
  public FilterRegistrationBean<RateLimitFilter> rateLimitFilter(RateLimitProperties rateLimitProperties,
      SecurityProperties securityProperties, com.example.reco.service.RateLimitStore rateLimitStore) {
    RateLimitFilter filter = new RateLimitFilter(rateLimitProperties, securityProperties, rateLimitStore);
    FilterRegistrationBean<RateLimitFilter> bean = new FilterRegistrationBean<>();
    bean.setFilter(filter);
    bean.addUrlPatterns("/api/*");
    bean.setOrder(2);
    return bean;
  }
}
