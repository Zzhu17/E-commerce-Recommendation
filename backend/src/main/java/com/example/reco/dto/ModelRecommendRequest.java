package com.example.reco.dto;

import java.util.List;
import java.util.Map;

public record ModelRecommendRequest(
    String requestId,
    String userId,
    String scene,
    int numItems,
    List<String> candidateItems,
    Map<String, Object> context
) {}
