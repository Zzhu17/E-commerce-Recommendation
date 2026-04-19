package com.example.reco;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class RecoApiApplication {
  public static void main(String[] args) {
    SpringApplication.run(RecoApiApplication.class, args);
  }
}
