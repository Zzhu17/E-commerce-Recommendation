package com.example.reco.config;

import java.util.Set;

public record AuthContext(
    String subject,
    Set<String> roles
) {}
