package com.example.reco.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record CandidateUpsertRequest(
    @NotBlank
    @Size(min = 3, max = 64)
    @Pattern(regexp = "^[a-zA-Z0-9_-]+$")
    String userId,
    @NotBlank
    @Pattern(regexp = "home|detail|cart|profile|search")
    String scene,
    @NotBlank
    @Size(min = 1, max = 64)
    @Pattern(regexp = "^[a-zA-Z0-9_-]+$")
    String itemId,
    @NotNull Double score
) {}
