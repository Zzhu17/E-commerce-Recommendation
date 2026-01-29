package com.example.reco.dto;

import java.util.List;

public record RecommendationResponse(
    String requestId,
    String userId,
    String scene,
    String modelVersion,
    List<RecommendationItem> items,
    Integer ttlSeconds
) {}
