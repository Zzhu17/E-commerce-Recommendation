package com.example.reco.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;

public record CandidateUpsertRequest(
    @NotBlank String userId,
    @NotBlank
    @Pattern(regexp = "home|detail|cart|profile|search")
    String scene,
    @NotBlank String itemId,
    @NotNull Double score
) {}
