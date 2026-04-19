package com.example.reco.controller;

import com.example.reco.dto.CandidateRow;
import com.example.reco.dto.CandidateUpsertBatch;
import com.example.reco.dto.FeedbackEvent;
import com.example.reco.dto.UserDeletionRequest;
import com.example.reco.service.AdminAccessService;
import com.example.reco.service.AdminAuditService;
import com.example.reco.service.CandidateAdminService;
import com.example.reco.service.FeedbackAdminService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import java.util.List;
import java.util.Map;
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
  private final AdminAccessService adminAccessService;
  private final AdminAuditService adminAuditService;

  public AdminController(
      CandidateAdminService candidateAdminService,
      FeedbackAdminService feedbackAdminService,
      AdminAccessService adminAccessService,
      AdminAuditService adminAuditService) {
    this.candidateAdminService = candidateAdminService;
    this.feedbackAdminService = feedbackAdminService;
    this.adminAccessService = adminAccessService;
    this.adminAuditService = adminAuditService;
  }

  @PostMapping("/candidates")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void upsertCandidates(@Valid @RequestBody CandidateUpsertBatch batch, HttpServletRequest request) {
    adminAccessService.requireWriteRole(request);
    candidateAdminService.upsert(batch.getItems());
    adminAuditService.log(
        adminAccessService.currentAuth(request).subject(),
        "candidate_batch_upsert",
        "items=" + batch.getItems().size()
    );
  }

  @GetMapping("/candidates")
  public List<CandidateRow> listCandidates(
      @RequestParam("userId") @NotBlank String userId,
      @RequestParam("scene") @NotBlank String scene,
      @RequestParam(value = "limit", defaultValue = "50") @Min(1) @Max(500) int limit,
      HttpServletRequest request
  ) {
    adminAccessService.requireReadRole(request);
    return candidateAdminService.list(userId, scene, limit);
  }

  @GetMapping("/feedback")
  public List<FeedbackEvent> listFeedback(
      @RequestParam("userId") @NotBlank String userId,
      @RequestParam(value = "limit", defaultValue = "50") @Min(1) @Max(500) int limit,
      HttpServletRequest request
  ) {
    adminAccessService.requireReadRole(request);
    List<FeedbackEvent> events = feedbackAdminService.listByUser(userId, limit);
    adminAuditService.log(
        adminAccessService.currentAuth(request).subject(),
        "feedback_export",
        "userId=" + userId + ",rows=" + events.size()
    );
    return events;
  }

  @PostMapping("/privacy/delete-user")
  public Map<String, Object> deleteUserData(@Valid @RequestBody UserDeletionRequest requestBody, HttpServletRequest request) {
    adminAccessService.requirePlatformAdmin(request);
    int deletedRows = feedbackAdminService.deleteByUserToken(requestBody.userToken(), requestBody.reason());
    return Map.of("userToken", requestBody.userToken(), "deletedFeedbackRows", deletedRows);
  }
}
