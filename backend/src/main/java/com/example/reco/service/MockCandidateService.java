package com.example.reco.service;

import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.IntStream;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "candidate.source", havingValue = "mock")
public class MockCandidateService implements CandidateService {
  @Override
  public List<String> getCandidates(String userId, String scene, int limit) {
    int size = Math.max(1, limit);
    int offset = ThreadLocalRandom.current().nextInt(0, 1000);
    return IntStream.range(0, size)
        .mapToObj(i -> "p" + String.format("%03d", offset + i + 1))
        .toList();
  }
}
