package com.example.reco.dto;

import jakarta.validation.constraints.NotBlank;

public record UserDeletionRequest(
    @NotBlank String userToken,
    String reason
) {
}
