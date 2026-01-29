package com.example.reco.dto;

public record RecommendationItem(
    String itemId,
    double score,
    String reason,
    int rank
) {}
