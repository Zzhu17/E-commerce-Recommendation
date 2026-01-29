package com.example.reco.service;

import com.example.reco.dto.FeedbackRequest;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "feedback.sink", havingValue = "file")
public class FileFeedbackSink implements FeedbackSink {
  private final Path sinkPath;
  private final ObjectMapper objectMapper = new ObjectMapper();

  public FileFeedbackSink(@Value("${feedback.sink-path}") String sinkPath) {
    this.sinkPath = Path.of(sinkPath);
  }

  @Override
  public void write(FeedbackRequest request) {
    try {
      Files.createDirectories(sinkPath.getParent());
      String line = objectMapper.writeValueAsString(request) + System.lineSeparator();
      Files.writeString(sinkPath, line, StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    } catch (JsonProcessingException e) {
      throw new RuntimeException("failed to serialize feedback", e);
    } catch (IOException e) {
      throw new RuntimeException("failed to persist feedback", e);
    }
  }
}
