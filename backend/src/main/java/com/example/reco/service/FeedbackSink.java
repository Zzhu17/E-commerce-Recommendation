package com.example.reco.service;

import com.example.reco.dto.FeedbackRequest;

public interface FeedbackSink {
  void write(FeedbackRequest request);
}
