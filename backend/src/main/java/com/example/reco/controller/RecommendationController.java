package com.example.reco.controller;

import com.example.reco.dto.FeedbackRequest;
import com.example.reco.dto.RecommendationResponse;
import com.example.reco.service.FeedbackSink;
import com.example.reco.service.RecommendationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
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
@RequestMapping("/api")
@Validated
@Tag(name = "Recommendations")
public class RecommendationController {
  private final RecommendationService service;
  private final FeedbackSink feedbackSink;

  public RecommendationController(RecommendationService service, FeedbackSink feedbackSink) {
    this.service = service;
    this.feedbackSink = feedbackSink;
  }

  @Operation(summary = "Get recommendations")
  @ApiResponse(responseCode = "200", description = "OK",
      content = @Content(schema = @Schema(implementation = RecommendationResponse.class)))
  @GetMapping("/recommendations")
  public RecommendationResponse getRecommendations(
      @Parameter(description = "User ID")
      @RequestParam("userId") @NotBlank String userId,
      @Parameter(description = "Scene", example = "home")
      @RequestParam("scene") @NotBlank String scene,
      @Parameter(description = "Number of items", example = "10")
      @RequestParam(value = "size", defaultValue = "10") @Min(1) @Max(50) int size,
      @Parameter(description = "Optional request ID")
      @RequestParam(value = "requestId", required = false) String requestId
  ) {
    return service.getRecommendations(requestId, userId, scene, size);
  }

  @Operation(summary = "Feedback event")
  @ApiResponse(responseCode = "204", description = "No Content")
  @PostMapping("/feedback")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void feedback(@Valid @RequestBody FeedbackRequest request) {
    feedbackSink.write(request);
  }
}
