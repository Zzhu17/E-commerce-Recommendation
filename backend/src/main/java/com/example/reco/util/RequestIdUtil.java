package com.example.reco.util;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.ThreadLocalRandom;
import java.util.regex.Pattern;
import org.slf4j.MDC;

public final class RequestIdUtil {
  private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");
  private static final Pattern PATTERN = Pattern.compile("^[a-zA-Z0-9_-]{1,64}$");

  private RequestIdUtil() {}

  public static String newRequestId() {
    int suffix = ThreadLocalRandom.current().nextInt(1000, 10000);
    return "req_" + LocalDateTime.now().format(FMT) + "_" + suffix;
  }

  public static boolean isValid(String requestId) {
    return requestId != null && PATTERN.matcher(requestId).matches();
  }

  public static String currentOrUnknown() {
    String current = MDC.get("requestId");
    return isValid(current) ? current : "unknown";
  }
}
