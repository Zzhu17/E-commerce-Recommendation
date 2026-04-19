package com.example.reco.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record UserDeletionRequest(
    @NotBlank
    @Size(max = 128)
    @Pattern(regexp = "^[a-zA-Z0-9:_-]+$")
    String userToken,
    @Size(max = 256)
    String reason
) {
}
