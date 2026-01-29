package com.example.reco.dto;

public record ErrorResponse(
    String requestId,
    String code,
    String message
) {}
