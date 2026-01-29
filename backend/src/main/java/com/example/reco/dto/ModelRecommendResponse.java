package com.example.reco.dto;

import java.util.List;

public record ModelRecommendResponse(
    String requestId,
    String modelVersion,
    List<ScoreItem> scores
) {}
