package com.example.reco.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.util.Map;

public record FeedbackRequest(
    @NotBlank
    @Size(max = 64)
    @Pattern(regexp = "^[a-zA-Z0-9_-]+$")
    String requestId,
    @NotBlank
    @Size(min = 3, max = 64)
    @Pattern(regexp = "^[a-zA-Z0-9_-]+$")
    String userId,
    @NotBlank
    @Size(min = 1, max = 64)
    @Pattern(regexp = "^[a-zA-Z0-9_-]+$")
    String itemId,
    @NotBlank
    @Pattern(regexp = "exposure|click|cart|purchase|dislike")
    String eventType,
    @NotBlank
    @Pattern(regexp = "home|detail|cart|profile|search")
    String scene,
    @Size(max = 32)
    @Pattern(regexp = "^[a-zA-Z0-9._-]*$")
    String modelVersion,
    @NotNull Long ts,
    @ValidFeedbackExtra
    Map<String, Object> extra
) {}
