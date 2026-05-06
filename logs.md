# Logging Architecture

## Pipeline

```
Your App (SLF4J + Logback)
    ↓ writes JSON to file
/app/logs/modulith.log
    ↓ Filebeat tails the file
Filebeat container
    ↓ ships to
Elasticsearch (indexes & stores)
    ↓ visualized in
Kibana (search, filter, dashboards)
```

---

## Layer 1: Dependencies

**`pom.xml`** — two additions:

- **`logstash-logback-encoder`** — makes Logback output structured JSON instead of plain text. Each log line becomes a JSON object with `@timestamp`, `level`, `message`, `logger_name`, `thread_name`, plus any MDC fields. This is what Filebeat and Elasticsearch understand natively.
- **`aspectjweaver`** — enables Spring AOP proxy weaving, required for the `@Aspect` classes to intercept method calls at runtime.

---

## Layer 2: Logback Configuration

**`Modulith/src/main/resources/logback-spring.xml`** — replaces Spring Boot's default logging config. Defines two appenders:

**CONSOLE appender** — human-readable output for local development:
```
2026-05-04 13:30:15.123 INFO  [http-nio-8081-exec-1] [a3f2b1c9] [user-uuid] ControllerLoggingAspect - >>> GET /bookings/123
```
The `[a3f2b1c9]` is the requestId from MDC, `[user-uuid]` is the userId. If you're reading Docker logs or running locally, this is what you see.

**JSON_FILE appender** — writes to `/app/logs/modulith.log` as one JSON object per line:
```json
{"@timestamp":"2026-05-04T13:30:15.123","level":"INFO","message":">>> GET /bookings/123","requestId":"a3f2b1c9","userId":"user-uuid","module":"booking","logger_name":"c.t.m.c.l.ControllerLoggingAspect","application":"modulith"}
```
This is what Filebeat reads and ships to Elasticsearch. The `LogstashEncoder` automatically includes MDC fields as top-level JSON keys.

**Log levels configured:**
- `com.tskhra.modulith` → INFO (your app code)
- `com.tskhra.modulith.common.logging` → DEBUG (so ServiceLoggingAspect debug logs are visible)
- `org.springframework`, `org.hibernate`, `org.apache.kafka`, etc. → WARN (reduces framework noise)

**Rolling policy:** Files rotate daily, max 50MB per file, 7 days retention, 500MB total cap.

---

## Layer 3: MDC Filter (Request Correlation)

**`common/logging/MdcFilter.java`** — a servlet filter registered in the Spring Security filter chain *after* `BearerTokenAuthenticationFilter`.

For every HTTP request, it:
1. **requestId** — checks for an incoming `X-Request-Id` header (from a load balancer or API gateway). If absent, generates a short UUID like `a3f2b1c9`. Also sets it as a response header so the client can correlate.
2. **userId** — reads the JWT from `SecurityContextHolder` (which is populated by Spring Security's bearer token filter that runs before this filter). Extracts the `sub` claim — this is the Keycloak user ID.
3. **module** — derives from the request URI: `/bookings/*` → `booking`, `/users/*` → `user`, `/trade-offers/*` → `trade`, etc.

All three are put into SLF4J's **MDC** (Mapped Diagnostic Context). MDC is a thread-local map — any log statement made during this request automatically includes these fields. The `finally` block clears MDC so the next request on the same thread doesn't inherit stale values.

**Why it's registered after BearerTokenAuthenticationFilter:** If it ran before authentication, `SecurityContextHolder` would be empty and we couldn't extract the userId.

**`common/logging/WebSocketMdcInterceptor.java`** — same concept but for WebSocket/STOMP messages. The servlet filter doesn't cover WebSocket frames. This `ChannelInterceptor` reads the `userId` from session attributes (already set by `TokenAuthInterceptor` during the WebSocket handshake) and sets MDC fields. Registered in `WebSocketConfiguration.configureClientInboundChannel()`.

---

## Layer 4: AOP Logging Aspects

These are the "automatic" logging — no manual `log.info()` needed in each controller/service.

**How Spring AOP works:** At startup, Spring creates proxy wrappers around your beans. When a method is called, the proxy intercepts it, runs the aspect's `@Around` advice, then calls the actual method. This is transparent to your code.

### ControllerLoggingAspect.java

**Location:** `common/logging/ControllerLoggingAspect.java`

**Pointcut:** `within(@RestController *) && within(com.tskhra.modulith..*)`
— intercepts every method in every class annotated with `@RestController` in your application.

**What it logs (INFO level):**
```
>>> GET /bookings/123?status=AWAITING -> BookingController.getAwaitingBookings()
<<< GET /bookings/123 -> 200 (45ms)
```

On entry: HTTP method, URI, query string, controller class name, method name.
On exit: HTTP method, URI, response status (extracted from `ResponseEntity`), execution duration.
On exception: logs at WARN with the exception class name, then re-throws.

**What it does NOT log:** Request/response bodies — intentionally omitted to avoid leaking passwords, tokens, or PII.

### ServiceLoggingAspect.java

**Location:** `common/logging/ServiceLoggingAspect.java`

**Pointcut:** `within(@Service *) && within(com.tskhra.modulith..*)`
— intercepts every public method in every `@Service` class.

**What it logs (DEBUG level):**
```
==> BookingService.createBooking()
<== BookingService.createBooking() completed in 120ms
```

At DEBUG level, so it's visible when developing but doesn't flood production logs. **Exception:** if a method takes longer than 500ms, it logs at WARN:
```
<== BookingService.createBooking() completed in 1200ms (SLOW)
```

This helps you spot performance issues in Kibana by filtering `level: WARN` + `logger_name: ServiceLoggingAspect`.

**Why separate from controllers:** Controllers are the external API boundary (INFO) — you always want to see them. Services are internal implementation (DEBUG) — you only want them when debugging. You can toggle each independently via log levels.

---

## Layer 5: GlobalExceptionHandler Logging

**`common/exception/GlobalExceptionHandler.java`** — previously caught all exceptions and returned error responses but logged nothing. Now every handler logs:

- **Client errors (4xx)** — `log.warn(...)` without stack traces:
  ```
  WARN  Not found: Booking not found
  WARN  Unauthorized: Invalid signature.
  WARN  Validation failed: [name: must not be blank, email: invalid format]
  ```

- **Unexpected errors (500)** — `log.error(...)` with full stack trace via the catch-all `@ExceptionHandler(Exception.class)`:
  ```
  ERROR Unhandled exception: NullPointerException at BookingService.java:123
  [full stack trace]
  ```

Since MDC is active, every exception log automatically includes `requestId` and `userId`, so you can trace exactly which user hit which error on which request.

---

## Layer 6: Manual Business Event Logging

AOP tells you *what methods were called*. Manual logging tells you *what happened in business terms*.

### BookingService.java
```
Booking created: bookingId={}, userId={}, serviceId={}, businessId={}, date={}, startTime={}
Booking approved: bookingId={}, approvedBy={}
Booking rejected: bookingId={}, rejectedBy={}
Booking cancelled by business: bookingId={}, cancelledBy={}
Booking cancelled by user: bookingId={}, userId={}
```

### TradeService.java
```
Trade offer created: offerId={}, offererId={}, responderId={}, itemCount={}
Trade offer accepted: offerId={}, responderId={}
Trade offer rejected: offerId={}, responderId={}
Trade offer withdrawn: offerId={}, offererId={}
Counter-offer created: originalOfferId={}, counterOfferId={}
Trade offer cancelled: offerId={}, cancelledBy={}
Handoff confirmed: offerId={}, confirmedBy={}
Trade completed: offerId={}
```

### ChainTradeService.java
```
Chain trade proposed: chainId={}, initiatorId={}, participantCount={}
Chain trade accepted by participant: chainId={}, userId={}
Chain trade activated: chainId={}, itemCount={}
Chain trade rejected: chainId={}, rejectedBy={}
Chain handoff confirmed: chainId={}, confirmedBy={}
Chain trade completed: chainId={}
```

### CredentialService.java
```
Device registered: deviceId={}, userId={}
Biometric login failed: deviceId={}, type={}     (WARN level)
Biometric login successful: deviceId={}, type={}
```

### TokenAuthInterceptor.java
WebSocket handshake authentication events (previously commented out, now re-enabled).

These manual logs use SLF4J's `{}` placeholder syntax — values are only string-formatted if the log level is enabled, avoiding unnecessary work.

---

## Layer 7: Infrastructure

### Dockerfile
Added `RUN mkdir -p /app/logs` so the log directory exists when the app starts.

### docker-compose.yml
- **`modulith_logs` volume** — shared named volume mounted in both the `modulith` container (`/app/logs`) and the `filebeat` container (`/app/logs:ro`). The app writes, Filebeat reads.
- **Kibana** — uncommented, depends on Elasticsearch health check. Available at port `5601`.
- **Filebeat** — runs with `--strict.perms=false` to skip config file ownership checks (avoids `chown root` issues in CI/CD).

### filebeat/filebeat.yml
- `type: filestream` (v9 replacement for deprecated `log` input)
- `ndjson` parser — tells Filebeat the log file is newline-delimited JSON, parses fields to top level
- Outputs to Elasticsearch at `modulith-logs-YYYY.MM.DD` daily indices
- Template and ILM setup disabled — Elasticsearch auto-creates indices

---

## How It All Connects — A Single Request's Journey

1. User calls `POST /bookings` with a JWT
2. Spring Security validates the JWT, populates `SecurityContextHolder`
3. **MdcFilter** runs: generates `requestId=a3f2b1c9`, extracts `userId=abc-123`, sets `module=booking`
4. **ControllerLoggingAspect** fires: logs `>>> POST /bookings -> BookingController.createBooking()`
5. **ServiceLoggingAspect** fires: logs `==> BookingService.createBooking()` (DEBUG)
6. **BookingService** runs business logic, logs `Booking created: bookingId=42, userId=7, ...`
7. **ServiceLoggingAspect** logs `<== BookingService.createBooking() completed in 85ms` (DEBUG)
8. **ControllerLoggingAspect** logs `<<< POST /bookings -> 200 (90ms)`
9. **MdcFilter** clears MDC in `finally`
10. All 4 log lines are written to console (human-readable) AND `/app/logs/modulith.log` (JSON)
11. **Filebeat** tails the file, ships JSON to Elasticsearch
12. You see them in **Kibana** with `requestId=a3f2b1c9` linking them all together

If step 6 threw an exception instead:
- **GlobalExceptionHandler** catches it, logs `WARN Not found: Service not found` (with requestId + userId in MDC)
- **ControllerLoggingAspect** logs `<<< POST /bookings -> EXCEPTION HttpNotFoundException (45ms)`
- Both appear in Kibana, traceable by the same requestId

---

## Key Files

| File | Purpose |
|------|---------|
| `Modulith/pom.xml` | logstash-logback-encoder + aspectjweaver dependencies |
| `Modulith/src/main/resources/logback-spring.xml` | Console + JSON file appenders, log levels |
| `Modulith/src/main/java/com/tskhra/modulith/common/logging/MdcFilter.java` | HTTP request correlation (requestId, userId, module) |
| `Modulith/src/main/java/com/tskhra/modulith/common/logging/WebSocketMdcInterceptor.java` | WebSocket message correlation |
| `Modulith/src/main/java/com/tskhra/modulith/common/logging/ControllerLoggingAspect.java` | Auto-logs all controller requests/responses |
| `Modulith/src/main/java/com/tskhra/modulith/common/logging/ServiceLoggingAspect.java` | Auto-logs all service method calls |
| `Modulith/src/main/java/com/tskhra/modulith/common/exception/GlobalExceptionHandler.java` | Exception logging |
| `Modulith/src/main/java/com/tskhra/modulith/common/config/SecurityConfiguration.java` | MdcFilter registration |
| `Modulith/Dockerfile` | /app/logs directory creation |
| `docker-compose.yml` | Kibana + Filebeat services, log volume |
| `filebeat/filebeat.yml` | Filebeat → Elasticsearch config |
