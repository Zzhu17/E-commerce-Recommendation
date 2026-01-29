package com.example.reco.service;

import java.util.List;

public interface CandidateService {
  List<String> getCandidates(String userId, String scene, int limit);
}
