package com.example.reco.dto;

public record FeedbackEvent(
    String requestId,
    String userId,
    String itemId,
    String eventType,
    String scene,
    String modelVersion,
    long ts,
    String extra,
    String createdAt
) {}
