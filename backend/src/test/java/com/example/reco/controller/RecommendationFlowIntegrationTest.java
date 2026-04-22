package com.example.reco.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.reco.config.JwtAuthFilter;
import com.example.reco.config.RateLimitFilter;
import com.example.reco.config.RateLimitProperties;
import com.example.reco.config.RequestIdFilter;
import com.example.reco.config.SecurityProperties;
import com.example.reco.dto.ModelRecommendRequest;
import com.example.reco.dto.ModelRecommendResponse;
import com.example.reco.dto.RecommendationItem;
import com.example.reco.dto.ScoreItem;
import com.example.reco.service.CandidateService;
import com.example.reco.service.FeedbackSink;
import com.example.reco.service.JwtAuthService;
import com.example.reco.service.ModelClient;
import com.example.reco.service.RateLimitStore;
import com.example.reco.service.RecommendationCache;
import com.example.reco.service.RecommendationService;
import com.example.reco.service.SecurityMonitoringService;
import com.example.reco.config.ModelProperties;
import com.example.reco.config.RecoCacheProperties;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Base64;
import java.util.List;
import java.util.Map;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

class RecommendationFlowIntegrationTest {
  @Test
  void explicitRequestIdStaysConsistentAcrossHeaderBodyAndModel() throws Exception {
    var fixture = fixture();

    when(fixture.candidateService.getCandidates("u123", "home", 10)).thenReturn(List.of("p001"));
    when(fixture.modelClient.recommend(any())).thenAnswer(invocation -> {
      ModelRecommendRequest request = invocation.getArgument(0);
      return new ModelRecommendResponse(request.requestId(), "v1", List.of(new ScoreItem("p001", 0.9)));
    });

    MvcResult result = fixture.mockMvc.perform(
            get("/api/recommendations")
                .queryParam("userId", "u123")
                .queryParam("scene", "home")
                .queryParam("size", "2")
                .queryParam("requestId", "req_query")
                .header("Authorization", "Bearer " + fixture.tokenWithRoles("ops_read"))
                .accept(MediaType.APPLICATION_JSON)
        )
        .andExpect(status().isOk())
        .andExpect(header().string(RequestIdFilter.HEADER, "req_query"))
        .andExpect(jsonPath("$.requestId").value("req_query"))
        .andReturn();

    ArgumentCaptor<ModelRecommendRequest> captor = ArgumentCaptor.forClass(ModelRecommendRequest.class);
    org.mockito.Mockito.verify(fixture.modelClient).recommend(captor.capture());
    assertEquals("req_query", captor.getValue().requestId());
    assertNotNull(result.getResponse().getContentAsString());
  }

  @Test
  void generatedRequestIdStaysConsistentAcrossHeaderBodyAndModel() throws Exception {
    var fixture = fixture();

    when(fixture.candidateService.getCandidates("u123", "home", 10)).thenReturn(List.of("p001"));
    when(fixture.modelClient.recommend(any())).thenAnswer(invocation -> {
      ModelRecommendRequest request = invocation.getArgument(0);
      return new ModelRecommendResponse(request.requestId(), "v1", List.of(new ScoreItem("p001", 0.9)));
    });

    MvcResult result = fixture.mockMvc.perform(
            get("/api/recommendations")
                .queryParam("userId", "u123")
                .queryParam("scene", "home")
                .queryParam("size", "2")
                .header("Authorization", "Bearer " + fixture.tokenWithRoles("ops_read"))
                .accept(MediaType.APPLICATION_JSON)
        )
        .andExpect(status().isOk())
        .andExpect(header().exists(RequestIdFilter.HEADER))
        .andReturn();

    String requestId = result.getResponse().getHeader(RequestIdFilter.HEADER);
    ArgumentCaptor<ModelRecommendRequest> captor = ArgumentCaptor.forClass(ModelRecommendRequest.class);
    org.mockito.Mockito.verify(fixture.modelClient).recommend(captor.capture());
    assertEquals(requestId, captor.getValue().requestId());
    assertEquals(requestId, extractJsonField(result.getResponse().getContentAsString(), "requestId"));
  }

  private TestFixture fixture() {
    CandidateService candidateService = mock(CandidateService.class);
    ModelClient modelClient = mock(ModelClient.class);
    FeedbackSink feedbackSink = mock(FeedbackSink.class);
    RateLimitStore rateLimitStore = mock(RateLimitStore.class);
    when(rateLimitStore.allow(any(), anyInt(), anyInt())).thenReturn(true);

    SecurityProperties securityProperties = new SecurityProperties();
    securityProperties.setJwtSecret("test-secret");
    JwtAuthService jwtAuthService = new JwtAuthService(securityProperties);
    SecurityMonitoringService monitoring = mock(SecurityMonitoringService.class);

    RateLimitProperties rateLimitProperties = new RateLimitProperties();
    rateLimitProperties.setEnabled(true);

    RecommendationService service = new RecommendationService(
        new ModelProperties(),
        candidateService,
        modelClient,
        new RecommendationCache(new RecoCacheProperties())
    );
    RecommendationController controller = new RecommendationController(service, feedbackSink);
    MockMvc mockMvc = MockMvcBuilders.standaloneSetup(controller)
        .setControllerAdvice(new ApiExceptionHandler())
        .addFilters(
            new RequestIdFilter(),
            new JwtAuthFilter(securityProperties, jwtAuthService, rateLimitStore, monitoring),
            new RateLimitFilter(rateLimitProperties, rateLimitStore)
        )
        .build();

    return new TestFixture(mockMvc, candidateService, modelClient, securityProperties);
  }

  private String extractJsonField(String body, String field) {
    String marker = "\"" + field + "\":\"";
    int start = body.indexOf(marker);
    int valueStart = start + marker.length();
    return body.substring(valueStart, body.indexOf('"', valueStart));
  }

  private record TestFixture(
      MockMvc mockMvc,
      CandidateService candidateService,
      ModelClient modelClient,
      SecurityProperties securityProperties
  ) {
    private String tokenWithRoles(String... roles) throws Exception {
      String header = base64Url("{\"alg\":\"HS256\",\"typ\":\"JWT\"}");
      long exp = Instant.now().plusSeconds(300).getEpochSecond();
      String payload = base64Url("{\"iss\":\"" + securityProperties.getIssuer()
          + "\",\"aud\":\"" + securityProperties.getAudience()
          + "\",\"sub\":\"ops-user\",\"exp\":" + exp
          + ",\"roles\":" + jsonArray(roles) + "}");
      String signature = sign(header + "." + payload, securityProperties.getJwtSecret());
      return header + "." + payload + "." + signature;
    }

    private String jsonArray(String[] roles) {
      StringBuilder builder = new StringBuilder("[");
      for (int i = 0; i < roles.length; i++) {
        if (i > 0) {
          builder.append(',');
        }
        builder.append('"').append(roles[i]).append('"');
      }
      return builder.append(']').toString();
    }

    private String base64Url(String raw) {
      return Base64.getUrlEncoder().withoutPadding().encodeToString(raw.getBytes(StandardCharsets.UTF_8));
    }

    private String sign(String data, String secret) throws Exception {
      Mac mac = Mac.getInstance("HmacSHA256");
      mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
      return Base64.getUrlEncoder().withoutPadding().encodeToString(mac.doFinal(data.getBytes(StandardCharsets.UTF_8)));
    }
  }

  private static int anyInt() {
    return org.mockito.ArgumentMatchers.anyInt();
  }
}
