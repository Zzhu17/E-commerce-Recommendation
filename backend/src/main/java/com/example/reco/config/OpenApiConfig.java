package com.example.reco.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {
  @Bean
  public OpenAPI recoOpenApi() {
    return new OpenAPI()
        .info(new Info()
            .title("Recommendation API")
            .version("0.1.0")
            .description("Frontend -> Spring API for recommendations and feedback"));
  }
}
