package com.example.reco.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;

public record FeedbackRequest(
    @NotBlank String requestId,
    @NotBlank String userId,
    @NotBlank String itemId,
    @NotBlank
    @Pattern(regexp = "exposure|click|cart|purchase|dislike")
    String eventType,
    @NotBlank
    @Pattern(regexp = "home|detail|cart|profile|search")
    String scene,
    String modelVersion,
    @NotNull Long ts,
    Object extra
) {}
