package com.example.reco.config;

import com.example.reco.service.JwtAuthService;
import com.example.reco.service.RateLimitStore;
import com.example.reco.service.SecurityMonitoringService;
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
      RateLimitStore rateLimitStore,
      SecurityMonitoringService securityMonitoringService) {
    GatewayProtectionFilter filter = new GatewayProtectionFilter(gatewayProtectionProperties, rateLimitStore, securityMonitoringService);
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
      RateLimitStore rateLimitStore,
      SecurityMonitoringService securityMonitoringService) {
    JwtAuthFilter filter = new JwtAuthFilter(securityProperties, jwtAuthService, rateLimitStore, securityMonitoringService);
    FilterRegistrationBean<JwtAuthFilter> bean = new FilterRegistrationBean<>();
    bean.setFilter(filter);
    bean.addUrlPatterns("/api/*", "/actuator/*");
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
    bean.addUrlPatterns("/api/*", "/actuator/*");
    bean.setOrder(3);
    return bean;
  }

  @Bean
  public FilterRegistrationBean<StructuredAccessLogFilter> structuredAccessLogFilter() {
    FilterRegistrationBean<StructuredAccessLogFilter> bean = new FilterRegistrationBean<>();
    bean.setFilter(new StructuredAccessLogFilter());
    bean.addUrlPatterns("/api/*", "/actuator/*");
    bean.setOrder(4);
    return bean;
  }
}
