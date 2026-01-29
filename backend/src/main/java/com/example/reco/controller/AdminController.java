package com.example.reco.controller;

import com.example.reco.dto.CandidateRow;
import com.example.reco.dto.CandidateUpsertBatch;
import com.example.reco.dto.FeedbackEvent;
import com.example.reco.service.CandidateAdminService;
import com.example.reco.service.FeedbackAdminService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin")
@Validated
public class AdminController {
  private final CandidateAdminService candidateAdminService;
  private final FeedbackAdminService feedbackAdminService;

  public AdminController(CandidateAdminService candidateAdminService, FeedbackAdminService feedbackAdminService) {
    this.candidateAdminService = candidateAdminService;
    this.feedbackAdminService = feedbackAdminService;
  }

  @PostMapping("/candidates")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void upsertCandidates(@Valid @RequestBody CandidateUpsertBatch batch) {
    candidateAdminService.upsert(batch.getItems());
  }

  @GetMapping("/candidates")
  public List<CandidateRow> listCandidates(
      @RequestParam("userId") @NotBlank String userId,
      @RequestParam("scene") @NotBlank String scene,
      @RequestParam(value = "limit", defaultValue = "50") @Min(1) @Max(500) int limit
  ) {
    return candidateAdminService.list(userId, scene, limit);
  }

  @GetMapping("/feedback")
  public List<FeedbackEvent> listFeedback(
      @RequestParam("userId") @NotBlank String userId,
      @RequestParam(value = "limit", defaultValue = "50") @Min(1) @Max(500) int limit
  ) {
    return feedbackAdminService.listByUser(userId, limit);
  }
}
