package com.example.reco.util;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.ThreadLocalRandom;

public final class RequestIdUtil {
  private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");

  private RequestIdUtil() {}

  public static String newRequestId() {
    int suffix = ThreadLocalRandom.current().nextInt(1000, 10000);
    return "req_" + LocalDateTime.now().format(FMT) + "_" + suffix;
  }
}
