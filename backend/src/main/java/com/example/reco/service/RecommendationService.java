package com.example.reco.service;

import com.example.reco.config.ModelProperties;
import com.example.reco.dto.ModelRecommendRequest;
import com.example.reco.dto.ModelRecommendResponse;
import com.example.reco.dto.RecommendationItem;
import com.example.reco.dto.RecommendationResponse;
import com.example.reco.dto.ScoreItem;
import com.example.reco.util.RequestIdUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class RecommendationService {
  private final ModelProperties modelProperties;
  private final CandidateService candidateService;
  private final ModelClient modelClient;
  private final RecommendationCache recommendationCache;

  public RecommendationService(
      ModelProperties modelProperties,
      CandidateService candidateService,
      ModelClient modelClient,
      RecommendationCache recommendationCache
  ) {
    this.modelProperties = modelProperties;
    this.candidateService = candidateService;
    this.modelClient = modelClient;
    this.recommendationCache = recommendationCache;
  }

  public RecommendationResponse getRecommendations(String requestId, String userId, String scene, int size) {
    String rid = (requestId == null || requestId.isBlank()) ? RequestIdUtil.newRequestId() : requestId;
    String cacheKey = userId + "|" + scene + "|" + size;
    RecommendationResponse cached = recommendationCache.get(cacheKey);
    if (cached != null) {
      return cached;
    }

    List<String> candidateItems = candidateService.getCandidates(userId, scene, size * 5);
    if (candidateItems == null || candidateItems.isEmpty()) {
      candidateItems = fallbackCandidates(size * 5);
    }

    ModelRecommendRequest modelRequest = new ModelRecommendRequest(
        rid,
        userId,
        scene,
        size,
        candidateItems,
        Map.of("device", "web")
    );

    ModelRecommendResponse modelResponse = modelClient.recommend(modelRequest);

    if (modelResponse == null || modelResponse.scores() == null || modelResponse.scores().isEmpty()) {
      return fallbackResponse(rid, userId, scene, size, candidateItems);
    }

    List<RecommendationItem> items = new ArrayList<>();
    int rank = 1;
    for (ScoreItem score : modelResponse.scores()) {
      if (rank > size) break;
      items.add(new RecommendationItem(score.itemId(), score.score(), null, rank));
      rank++;
    }

    String modelVersion = modelResponse.modelVersion() != null
        ? modelResponse.modelVersion()
        : modelProperties.getDefaultVersion();

    RecommendationResponse response = new RecommendationResponse(
        rid,
        userId,
        scene,
        modelVersion,
        items,
        300
    );
    recommendationCache.put(cacheKey, response);
    return response;
  }

  private RecommendationResponse fallbackResponse(String requestId, String userId, String scene, int size, List<String> candidates) {
    List<RecommendationItem> items = new ArrayList<>();
    for (int i = 0; i < Math.min(size, candidates.size()); i++) {
      items.add(new RecommendationItem(candidates.get(i), 1.0 - i * 0.01, "fallback", i + 1));
    }
    RecommendationResponse response = new RecommendationResponse(
        requestId, userId, scene, modelProperties.getDefaultVersion(), items, 120);
    recommendationCache.put(userId + "|" + scene + "|" + size, response);
    return response;
  }

  private List<String> fallbackCandidates(int n) {
    List<String> candidates = new ArrayList<>();
    for (int i = 0; i < n; i++) {
      candidates.add("p" + String.format("%03d", i + 1));
    }
    return candidates;
  }
}
