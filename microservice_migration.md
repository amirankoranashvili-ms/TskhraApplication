# Microservices Migration Guide for Tskhra Application

## 1. Current State Assessment

Your modulith is in **good shape** for migration:
- **No circular dependencies** between modules
- **Denormalized IDs** (userId stored as `Long`, not JPA `@ManyToOne`) — this is huge
- **Event-driven communication** already in place via Spring ApplicationEventPublisher + Kafka
- **Kafka infrastructure** already running

**Pain points to address first:**
- `BookingService`, `ServiceService`, `BusinessService`, `BusinessImageService` all directly inject `UserService` — these must become API calls
- `ImageService` in `common` is shared by both user and booking modules
- Single PostgreSQL database for everything
- Shared `common` module (exceptions, config, security)

---

## 2. Repository Strategy

You have two options:

### Option A: Monorepo (Recommended for your team size)
```
tskhra/
├── services/
│   ├── user-service/
│   ├── booking-service/
│   ├── notification-service/
│   ├── messaging-service/
│   └── api-gateway/
├── libs/
│   ├── tskhra-common/        # shared DTOs, exceptions
│   └── tskhra-events/        # event contracts (Avro/Protobuf schemas)
├── infra/
│   ├── docker-compose.yml
│   ├── k8s/                  # or docker swarm configs
│   └── nginx/
└── pom.xml                   # parent POM with dependency management
```

**Why monorepo**: Easier refactoring, atomic cross-service changes, shared CI pipeline. Switch to polyrepo only when you have multiple teams owning different services.

### Option B: Polyrepo
One repo per service + a shared `tskhra-contracts` repo published to a Maven registry (GitHub Packages / Nexus). Use this when you have distinct teams.

**Recommendation**: Start with monorepo. Split repos later when organizational boundaries justify it.

---

## 3. Database Strategy

### Per-Service Databases (Target State)

| Service | Database | Rationale |
|---------|----------|-----------|
| user-service | `tskhra_users_db` | User, UserDevice, UserBiometricDevices, UserVerificationRequest, Admin |
| booking-service | `tskhra_bookings_db` | Business, Service, Booking, Resource, Category, City, Address, Schedule entities |
| notification-service | `tskhra_notifications_db` | FcmToken only |
| messaging-service | `tskhra_messaging_db` | Message entities |

### Migration Path (Phased)

**Phase 1 — Schema separation (still one Postgres instance):**
```sql
-- Create separate schemas within the same database
CREATE SCHEMA users;
CREATE SCHEMA bookings;
CREATE SCHEMA notifications;
CREATE SCHEMA messaging;

-- Move tables
ALTER TABLE users SET SCHEMA users;
ALTER TABLE user_devices SET SCHEMA users;
ALTER TABLE bookings SET SCHEMA bookings;
-- etc.
```
Each service connects with a schema-specific user that can only access its own schema. This catches cross-schema queries early.

**Phase 2 — Separate databases (still one Postgres server):**
Create separate databases. This is a data migration, not a code change — use `pg_dump`/`pg_restore` per schema.

**Phase 3 — Separate database servers (if needed for scaling):**
Only do this when you have actual scaling requirements.

### Handling Cross-Service Data

Your current `favoriteBusinessIds` in User is an `@ElementCollection` of business IDs. After split:
- **Option 1**: Keep it in user-service — it's just a set of IDs, no FK constraint needed
- **Option 2**: Move it to booking-service as a `UserFavorite(userId, businessId)` table

The `userId` columns in Booking, Business, FcmToken are already just `Long` fields — no schema changes needed. You just lose referential integrity (acceptable in microservices; enforce at the application layer).

---

## 4. Decoupling Cross-Module Service Calls

This is your **biggest refactoring task**. Currently:

```
BookingService → UserService.getUserByKeycloakId()
BusinessService → UserService.getUserByKeycloakId()
ServiceService → UserService.getUserByKeycloakId()
BusinessImageService → UserService.getUserByKeycloakId()
```

### Replace with: Internal REST/gRPC Calls + Caching

**Step 1**: Create a `UserClient` interface in booking-service:
```java
public interface UserClient {
    UserDto getUserByKeycloakId(String keycloakId);
    boolean userExists(String keycloakId);
}
```

**Step 2**: Implement via REST (or gRPC for lower latency):
```java
@Component
public class UserRestClient implements UserClient {
    private final RestClient restClient;

    public UserDto getUserByKeycloakId(String keycloakId) {
        return restClient.get()
            .uri("/internal/users/by-keycloak-id/{id}", keycloakId)
            .retrieve()
            .body(UserDto.class);
    }
}
```

**Step 3**: Add Redis caching to avoid constant round-trips:
```java
@Cacheable(value = "users", key = "#keycloakId")
public UserDto getUserByKeycloakId(String keycloakId) { ... }
```

**Step 4**: Handle failures with Circuit Breaker (Resilience4j):
```java
@CircuitBreaker(name = "userService", fallbackMethod = "fallback")
public UserDto getUserByKeycloakId(String keycloakId) { ... }
```

### Internal vs External APIs

Expose two sets of endpoints per service:
- `/api/v1/**` — external (JWT-authenticated, user-facing)
- `/internal/**` — service-to-service (mTLS or API key, not exposed through gateway)

---

## 5. Event-Driven Communication

You already have the foundation. Here's how to mature it:

### Event Contracts (Shared Library: `tskhra-events`)

```java
// In tskhra-events module (shared)
public record BookingStatusChangedEvent(
    Long bookingId,
    Long userId,
    Long businessId,
    String serviceName,
    BookingStatus oldStatus,
    BookingStatus newStatus,
    Instant occurredAt
) {}
```

Use **Avro or Protobuf** schemas for production (schema evolution, backward compatibility). For now, JSON with a shared library works.

### Kafka Topics

| Topic | Producer | Consumer(s) |
|-------|----------|-------------|
| `booking.status-changed` | booking-service | notification-service |
| `booking.created` | booking-service | notification-service |
| `user.registered` | user-service | booking-service (optional) |
| `user.profile-updated` | user-service | booking-service (cache invalidation) |

### Outbox Pattern (Critical for Reliability)

Your current `ApplicationEventPublisher` fires events in-memory. If the app crashes between DB commit and event publish, you lose events. Use the **Transactional Outbox Pattern**:

```java
// 1. Save event to outbox table in same transaction as business data
@Transactional
public Booking createBooking(BookingRequest request) {
    Booking booking = bookingRepository.save(new Booking(...));
    outboxRepository.save(new OutboxEvent("booking.created", serialize(booking)));
    return booking;
}

// 2. A separate poller/CDC reads outbox and publishes to Kafka
// Spring Modulith already does this! Use spring-modulith-events-kafka
```

Good news: **Spring Modulith's `@Externalized` already implements this** via `spring-modulith-events-jpa` + `spring-modulith-events-kafka`. Keep using it.

---

## 6. Shared `common` Module → Shared Libraries

Split your `common` module into:

### `tskhra-common` (Shared library, published to Maven)
- Exception classes (`HttpBadRequestException`, etc.)
- `ErrorResponse` model
- Custom validators (`@MinAge`, `@MaxAge`, `@ValidPassword`, etc.)
- Utility classes

### Per-Service Configuration (NOT shared)
- `SecurityConfiguration` → each service gets its own (they may have different public endpoints)
- `KeycloakConfiguration` → only in user-service
- `MinioConfiguration` → only in services that need file storage
- `SwaggerConfiguration` → each service gets its own

### `ImageService` Split
- User avatar operations → user-service (with its own Minio config)
- Business image operations → booking-service (with its own Minio config)
- Both can point to the same Minio instance, different buckets

---

## 7. API Gateway

Replace your current Nginx with **Spring Cloud Gateway** (or keep Nginx, but add service discovery):

### Option A: Spring Cloud Gateway (Recommended)
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/v1/users/**, /api/v1/auth/**
        - id: booking-service
          uri: lb://booking-service
          predicates:
            - Path=/api/v1/bookings/**, /api/v1/businesses/**, /api/v1/services/**
        - id: notification-service
          uri: lb://notification-service
          predicates:
            - Path=/api/v1/notifications/**
```

### Option B: Keep Nginx + Consul/Eureka
If you prefer Nginx, add service discovery so Nginx upstreams are dynamically registered.

### Gateway Responsibilities
- Route requests to correct service
- JWT validation (centralized — services trust the gateway)
- Rate limiting
- CORS handling (move out of individual services)

---

## 8. Service Discovery & Configuration

### Service Discovery: Spring Cloud Consul or Eureka
```yaml
# Each service registers itself
spring:
  cloud:
    consul:
      host: consul
      port: 8500
      discovery:
        service-name: ${spring.application.name}
```

### Centralized Configuration: Spring Cloud Config Server
```
config-server/
├── user-service.yml
├── booking-service.yml
├── notification-service.yml
└── application.yml          # shared defaults
```

Or use **HashiCorp Vault** for secrets + config files per environment.

---

## 9. Docker & Infrastructure

### Updated docker-compose.yml Structure

```yaml
services:
  # --- Infrastructure ---
  postgres:
    image: postgres:16
    # Multiple databases via init script
    volumes:
      - ./infra/init-databases.sh:/docker-entrypoint-initdb.d/init.sh

  kafka:
    image: confluentinc/cp-kafka:7.6.0

  redis:
    image: redis:7

  keycloak:
    image: quay.io/keycloak/keycloak:26.1

  minio:
    image: minio/minio

  # --- Application Services ---
  user-service:
    build: ./services/user-service
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/tskhra_users_db
    depends_on: [postgres, keycloak, redis, minio]

  booking-service:
    build: ./services/booking-service
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/tskhra_bookings_db
    depends_on: [postgres, kafka, redis]

  notification-service:
    build: ./services/notification-service
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/tskhra_notifications_db
    depends_on: [postgres, kafka]

  messaging-service:
    build: ./services/messaging-service
    depends_on: [redis]

  api-gateway:
    build: ./services/api-gateway
    ports:
      - "8080:8080"
    depends_on: [user-service, booking-service, notification-service]
```

### Init Script for Multiple Databases
```bash
#!/bin/bash
# infra/init-databases.sh
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE tskhra_users_db;
    CREATE DATABASE tskhra_bookings_db;
    CREATE DATABASE tskhra_notifications_db;
    CREATE DATABASE tskhra_messaging_db;
EOSQL
```

---

## 10. Observability (Critical for Microservices)

You **cannot** run microservices without proper observability. Add these:

### Distributed Tracing: Micrometer Tracing + Zipkin/Jaeger
```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-exporter-otlp</artifactId>
</dependency>
```
This propagates trace IDs across service calls so you can follow a request through all services.

### Centralized Logging: ELK Stack (you already have Elasticsearch + Kibana)
- Add a `traceId` field to all log entries
- Use structured JSON logging (Logback + logstash-encoder)

### Health Checks & Metrics: Spring Boot Actuator + Prometheus + Grafana
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health, prometheus, info
  endpoint:
    health:
      show-details: always
```

---

## 11. Migration Order (Phased Execution)

### Phase 0: Pre-Migration Refactoring (Do This NOW, In the Monolith)

1. **Eliminate direct `UserService` injection in booking_module** — replace with an interface (`UserClient`) that initially delegates to `UserService` locally. This lets you swap implementations later without changing business logic.
2. **Split `ImageService`** into user-specific and business-specific implementations
3. **Externalize all events to Kafka** (not just `BookingCreatedEvent`) — use `@Externalized` on all events
4. **Separate database schemas** within the existing database
5. **Add proper Flyway migrations** — you're currently using `hibernate.ddl-auto: update` which is dangerous for production
6. **Write integration tests** for module boundaries (you already have `ModularityTest`)

### Phase 1: Extract user-service
- Simplest module, no outbound service dependencies
- Exposes `/internal/users/**` for other services
- Owns Keycloak integration, KYC (Sumsub), biometric auth
- KeycloakUserRegistrationSpi still calls user-service (just change the URL)

### Phase 2: Extract booking-service
- Replace `UserClient` local implementation with REST client
- Owns all business/service/booking/resource entities
- Publishes events to Kafka
- Add circuit breaker for user-service calls

### Phase 3: Extract notification-service
- Already loosely coupled (event listener only)
- Consumes from Kafka topics
- Owns FcmToken storage
- Minimal effort

### Phase 4: Extract messaging-service
- WebSocket/STOMP service
- May need shared session state via Redis

### Phase 5: Add API Gateway
- Spring Cloud Gateway or continue with Nginx
- Centralize auth, routing, rate limiting

---

## 12. Checklist Before Going Live

| Item | Why |
|------|-----|
| Circuit breakers on all inter-service calls | Prevent cascade failures |
| Retry policies with exponential backoff | Handle transient failures |
| Health check endpoints on every service | Load balancer needs them |
| Distributed tracing (trace ID in every log) | Debug cross-service issues |
| Centralized logging | You can't SSH into 5 containers |
| Database connection pooling (HikariCP tuned) | Prevent connection exhaustion |
| Flyway migrations (not ddl-auto) | Reproducible schema changes |
| API versioning strategy | Breaking changes happen |
| Secret management (Vault or k8s secrets) | No more `.env` files |
| CI/CD per service | Independent deployability |
| Contract tests (Spring Cloud Contract or Pact) | Catch breaking API changes |
| Graceful shutdown (`server.shutdown=graceful`) | No dropped requests during deploy |

---

## Key Advice

**Don't migrate everything at once.** The phased approach above lets you validate each step. Your modulith is already well-structured — the Phase 0 refactoring inside the monolith is the most important step because it proves your boundaries are clean before you pay the operational cost of distributed systems.

Also: **microservices are an operational burden**. Make sure you have observability, CI/CD, and container orchestration (at minimum Docker Compose, ideally Kubernetes) sorted before extracting the first service. The code changes are the easy part — running and debugging 5 services instead of 1 is the hard part.