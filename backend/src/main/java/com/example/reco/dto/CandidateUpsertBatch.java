package com.example.reco.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;
import java.util.List;

public class CandidateUpsertBatch {
  @NotEmpty
  @Size(max = 200)
  @Valid
  private List<CandidateUpsertRequest> items;

  public List<CandidateUpsertRequest> getItems() {
    return items;
  }

  public void setItems(List<CandidateUpsertRequest> items) {
    this.items = items;
  }
}
