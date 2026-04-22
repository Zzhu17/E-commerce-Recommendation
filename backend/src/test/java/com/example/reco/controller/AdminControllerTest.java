package com.example.reco.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.example.reco.config.AuthContext;
import com.example.reco.dto.FeedbackEvent;
import com.example.reco.service.AdminAccessService;
import com.example.reco.service.AdminAuditService;
import com.example.reco.service.CandidateAdminService;
import com.example.reco.service.FeedbackAdminService;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;

class AdminControllerTest {
  @Test
  void feedbackExportAuditDoesNotLogRawUserId() {
    CandidateAdminService candidateAdminService = mock(CandidateAdminService.class);
    FeedbackAdminService feedbackAdminService = mock(FeedbackAdminService.class);
    AdminAccessService adminAccessService = mock(AdminAccessService.class);
    AdminAuditService adminAuditService = mock(AdminAuditService.class);
    AdminController controller = new AdminController(
        candidateAdminService,
        feedbackAdminService,
        adminAccessService,
        adminAuditService
    );

    MockHttpServletRequest request = new MockHttpServletRequest();
    when(feedbackAdminService.listByUser("u123", 10)).thenReturn(List.of(
        new FeedbackEvent("req1", "tok_x", "p1", "click", "home", "v1", 1L, null, "now")
    ));
    when(adminAccessService.currentAuth(request)).thenReturn(new AuthContext("ops-user", Set.of("ops_read")));

    List<FeedbackEvent> events = controller.listFeedback("u123", 10, request);

    assertEquals(1, events.size());
    verify(adminAccessService).requireReadRole(request);
    verify(adminAuditService).log("ops-user", "feedback_export", "rows=1");
  }
}
