package com.example.reco.dto;

public record CandidateRow(
    String itemId,
    double score,
    String updatedAt
) {}
