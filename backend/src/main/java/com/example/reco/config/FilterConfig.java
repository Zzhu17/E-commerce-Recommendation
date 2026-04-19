package com.example.reco.config;

import com.example.reco.service.JwtAuthService;
import com.example.reco.service.RateLimitStore;
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
  public FilterRegistrationBean<GatewayProtectionFilter> gatewayProtectionFilter(
      GatewayProtectionProperties gatewayProtectionProperties,
      RateLimitStore rateLimitStore) {
    GatewayProtectionFilter filter = new GatewayProtectionFilter(gatewayProtectionProperties, rateLimitStore);
    FilterRegistrationBean<GatewayProtectionFilter> bean = new FilterRegistrationBean<>();
    bean.setFilter(filter);
    bean.addUrlPatterns("/api/*", "/actuator/*");
    bean.setOrder(1);
    return bean;
  }

  @Bean
  public FilterRegistrationBean<JwtAuthFilter> jwtAuthFilter(
      SecurityProperties securityProperties,
      JwtAuthService jwtAuthService,
      RateLimitStore rateLimitStore) {
    JwtAuthFilter filter = new JwtAuthFilter(securityProperties, jwtAuthService, rateLimitStore);
    FilterRegistrationBean<JwtAuthFilter> bean = new FilterRegistrationBean<>();
    bean.setFilter(filter);
    bean.addUrlPatterns("/api/*");
    bean.setOrder(2);
    return bean;
  }

  @Bean
  public FilterRegistrationBean<RateLimitFilter> rateLimitFilter(
      RateLimitProperties rateLimitProperties,
      com.example.reco.service.RateLimitStore rateLimitStore) {
    RateLimitFilter filter = new RateLimitFilter(rateLimitProperties, rateLimitStore);
    FilterRegistrationBean<RateLimitFilter> bean = new FilterRegistrationBean<>();
    bean.setFilter(filter);
    bean.addUrlPatterns("/api/*");
    bean.setOrder(3);
    return bean;
  }
}
