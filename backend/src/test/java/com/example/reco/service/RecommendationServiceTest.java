package com.example.reco.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verifyNoInteractions;

import com.example.reco.config.ModelProperties;
import com.example.reco.config.RecoCacheProperties;
import com.example.reco.dto.RecommendationItem;
import com.example.reco.dto.RecommendationResponse;
import java.util.List;
import org.junit.jupiter.api.Test;

class RecommendationServiceTest {
  @Test
  void cacheHitGetsFreshRequestId() {
    ModelProperties modelProperties = new ModelProperties();
    CandidateService candidateService = mock(CandidateService.class);
    ModelClient modelClient = mock(ModelClient.class);
    RecoCacheProperties cacheProperties = new RecoCacheProperties();
    cacheProperties.setEnabled(true);
    RecommendationCache cache = new RecommendationCache(cacheProperties);
    RecommendationService service =
        new RecommendationService(modelProperties, candidateService, modelClient, cache);

    List<RecommendationItem> items = List.of(new RecommendationItem("p001", 0.9, null, 1));
    cache.put("u123|home|1", new RecommendationResponse("req_old", "u123", "home", "v1", items, 300));

    RecommendationResponse response = service.getRecommendations("req_new", "u123", "home", 1);

    assertEquals("req_new", response.requestId());
    assertEquals("u123", response.userId());
    assertSame(items, response.items());
    verifyNoInteractions(candidateService, modelClient);
  }
}
