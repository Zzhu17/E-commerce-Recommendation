package com.example.reco.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.verifyNoInteractions;

import com.example.reco.config.ModelProperties;
import com.example.reco.config.RecoCacheProperties;
import com.example.reco.dto.ModelRecommendResponse;
import com.example.reco.dto.RecommendationItem;
import com.example.reco.dto.RecommendationResponse;
import com.example.reco.dto.ScoreItem;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;

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
    MDC.put("requestId", "req_new");

    RecommendationResponse response = service.getRecommendations("u123", "home", 1);

    assertEquals("req_new", response.requestId());
    assertEquals("u123", response.userId());
    assertSame(items, response.items());
    verifyNoInteractions(candidateService, modelClient);
    MDC.remove("requestId");
  }

  @Test
  void usesCurrentRequestIdForModelAndResponse() {
    ModelProperties modelProperties = new ModelProperties();
    CandidateService candidateService = mock(CandidateService.class);
    ModelClient modelClient = mock(ModelClient.class);
    RecommendationService service =
        new RecommendationService(modelProperties, candidateService, modelClient, new RecommendationCache(new RecoCacheProperties()));

    when(candidateService.getCandidates("u123", "home", 10)).thenReturn(List.of("p001"));
    when(modelClient.recommend(any())).thenAnswer(invocation -> {
      var request = invocation.getArgument(0, com.example.reco.dto.ModelRecommendRequest.class);
      return new ModelRecommendResponse(request.requestId(), "v1", List.of(new ScoreItem("p001", 0.9)));
    });

    MDC.put("requestId", "req_ctx");
    RecommendationResponse response = service.getRecommendations("u123", "home", 2);

    assertEquals("req_ctx", response.requestId());
    assertEquals("v1", response.modelVersion());
    MDC.remove("requestId");
  }
}
