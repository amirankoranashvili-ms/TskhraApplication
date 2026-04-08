# Microservices Migration Guide — Part 2 (Detailed Answers)

---

## 1. Service Granularity — Refactoring Recommendations

### Current Module Sizes

| Module | Controllers | Services | Entities | Verdict |
|--------|------------|----------|----------|---------|
| booking_module | 8 | 8 | 11 | **Too large — split it** |
| user_module | 6 | 4 | 5 | Good size |
| notification_module | 1 | 1 | 1 | **Too small — merge or expand** |
| messaging_module | 1 | 0 (config only) | 0 | Standalone infra service |

### booking_module: Split Into 2 Services

Don't over-split. You're a solo developer — more services = more things to deploy, debug, and maintain. Split booking_module into **2 services**, not 5:

**business-service** (reference/catalog data + business management):
- Business, BusinessImage, BusinessSchedule, BusinessUnavailableSchedule, BusinessUnavailableOnetime
- Service (the bookable service entity), Resource
- Category, City, Address
- Why together: These are all managed by the business owner and tightly coupled via JPA relationships (`Business @OneToMany Service`, `Service @ManyToMany Resource`, `Business @OneToOne Address`, etc.)

**booking-service** (transactional booking flow):
- Booking entity only
- Booking creation, approval/rejection, cancellation
- References business-service data by ID (businessId, serviceId, resourceId)
- Why separate: Bookings are the high-write, high-contention part. Business catalog data is mostly read-heavy. Different scaling and caching strategies.

### notification_module: Merge FCM Token Management Into user-service

FCM tokens are tied to users (they have a `userId` field). Move `FcmToken` entity and `FcmTokenController` into user-service.

Keep the **notification-service** as a standalone Kafka consumer that:
- Listens to events from Kafka (`booking.status-changed`, etc.)
- Calls user-service to get FCM tokens for a given userId
- Sends push notifications via Firebase
- No database of its own — fully stateless (or with its own DB just for delivery tracking)

### messaging_module: Keep As-Is

WebSocket/STOMP broker. It's infrastructure, not business logic. Keep it as a standalone service.

### Final Service Map

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  user-service   │     │ business-service  │     │  booking-service    │
│                 │     │                   │     │                     │
│ User            │     │ Business          │     │ Booking             │
│ UserDevice      │     │ Service           │     │                     │
│ BiometricDevice │     │ Resource          │     │ gRPC → business-svc │
│ Verification    │     │ Category, City    │     │ gRPC → user-svc     │
│ Admin           │     │ Address           │     │                     │
│ FcmToken        │     │ Schedule entities │     │ Publishes → Kafka   │
│ Auth (Keycloak) │     │ BusinessImage     │     │                     │
│ KYC (Sumsub)    │     │                   │     │                     │
└────────┬────────┘     └────────┬──────────┘     └──────────┬──────────┘
         │                       │                            │
         │              ┌────────┴──────────┐                 │
         │              │                   │                 │
    ┌────▼────┐    ┌────▼─────┐      ┌──────▼──────┐   ┌─────▼─────┐
    │ Keycloak│    │  MinIO   │      │    Kafka    │   │   Redis   │
    └─────────┘    └──────────┘      └──────┬──────┘   └───────────┘
                                            │
                                   ┌────────▼─────────┐
                                   │notification-svc  │
                                   │ (stateless)      │
                                   │ Kafka consumer   │
                                   │ → Firebase FCM   │
                                   └──────────────────┘

                                   ┌──────────────────┐
                                   │ messaging-service │
                                   │ WebSocket/STOMP   │
                                   └──────────────────┘
```

**Total: 5 services** — manageable for a solo developer.

---

## 2. Monorepo — Why It's The Right Choice For You

**Monorepo is the correct choice.** Here's why it's especially right for a solo developer:

### Advantages For Solo Dev
- **Atomic changes**: When you change a gRPC contract, you update the proto file AND all affected services in one commit. No version mismatch nightmares.
- **Single CI pipeline**: One Jenkinsfile builds everything. No need to manage inter-repo build triggers.
- **Shared tooling**: One `.env`, one `docker-compose.yml`, one IDE project. You open one IntelliJ window, not five.
- **Refactoring is easy**: Move classes between services with IDE refactoring. Try doing that across repos.
- **No Maven publishing**: Shared libraries are just Maven modules — `mvn install` makes them available. No Nexus/GitHub Packages setup.

### When You Would Switch to Polyrepo
Only if/when you hire developers and assign service ownership. Until then, monorepo saves you hours of DevOps overhead every week.

### Recommended Monorepo Structure

```
tskhra/
├── pom.xml                          # Parent POM (dependency management)
├── docker-compose.yml               # Full stack
├── proto/                           # gRPC .proto files (shared)
│   ├── user.proto
│   ├── business.proto
│   └── booking.proto
├── libs/
│   ├── tskhra-common/               # Shared exceptions, validators, DTOs
│   │   └── pom.xml
│   └── tskhra-events/               # Kafka event contracts
│       └── pom.xml
├── services/
│   ├── user-service/
│   │   └── pom.xml                  # Depends on tskhra-common
│   ├── business-service/
│   │   └── pom.xml
│   ├── booking-service/
│   │   └── pom.xml
│   ├── notification-service/
│   │   └── pom.xml
│   ├── messaging-service/
│   │   └── pom.xml
│   └── api-gateway/
│       └── pom.xml
├── infra/
│   ├── nginx/
│   ├── keycloak/
│   └── init-databases.sh
├── Jenkinsfile
└── .env
```

### Parent POM Pattern
```xml
<project>
    <groupId>com.tskhra</groupId>
    <artifactId>tskhra-parent</artifactId>
    <packaging>pom</packaging>

    <modules>
        <module>libs/tskhra-common</module>
        <module>libs/tskhra-events</module>
        <module>services/user-service</module>
        <module>services/business-service</module>
        <module>services/booking-service</module>
        <module>services/notification-service</module>
        <module>services/messaging-service</module>
        <module>services/api-gateway</module>
    </modules>

    <dependencyManagement>
        <!-- Spring Boot BOM, Spring Cloud BOM, shared versions -->
    </dependencyManagement>
</project>
```

Build everything: `mvn clean package -DskipTests`
Build one service: `mvn -pl services/user-service -am clean package`

---

## 3. Database Instance Strategy — For a 16GB RAM Laptop

### Recommendation: 1 PostgreSQL Instance, Separate Databases

**One Postgres instance with multiple databases is the right call.** Here's the math:

| Component | Estimated RAM |
|-----------|--------------|
| PostgreSQL 16 (1 instance, 4 databases) | ~512MB–1GB |
| Keycloak | ~512MB |
| Redis | ~100MB |
| Kafka + Zookeeper | ~1.5GB |
| MinIO | ~256MB |
| Elasticsearch + Kibana | ~2–3GB |
| 5 Spring Boot services (@256MB each) | ~1.3GB |
| API Gateway | ~256MB |
| OS + system overhead | ~2GB |
| **Total** | **~8.5–9GB** |

Adding a second Postgres instance saves nothing meaningful and adds 300–500MB overhead per instance.

### Configuration

```yaml
# Single postgres in docker-compose.yml
postgres:
  image: postgres:16
  environment:
    POSTGRES_USER: tskhra_admin
    POSTGRES_PASSWORD: ${DB_PASSWORD}
  volumes:
    - ./infra/init-databases.sh:/docker-entrypoint-initdb.d/init.sh
    - pgdata:/var/lib/postgresql/data
  # Tune for 16GB machine
  command: >
    postgres
    -c shared_buffers=256MB
    -c effective_cache_size=512MB
    -c work_mem=4MB
    -c max_connections=100
```

### Why NOT 2-3 Instances
- Each Postgres instance has ~150-300MB base overhead regardless of load
- On 16GB with your full stack, RAM is tight — don't waste it on duplicate processes
- The whole point of separate databases is **logical isolation**, not physical. One instance with 4 databases gives you:
  - Separate connection strings per service
  - No cross-database queries possible
  - Independent backup/restore per database
  - Same security guarantees as separate instances

### When You Would Add a Second Instance
Only if one database has dramatically different performance requirements (e.g., messaging needs a high-write-optimized config while bookings need read-optimized). Not your case right now.

---

## 4. gRPC + Kafka + JWT Claims Strategy

### gRPC Setup

#### Proto Files (shared in `proto/` directory)

```protobuf
// proto/user.proto
syntax = "proto3";
package com.tskhra.user;

option java_multiple_files = true;
option java_package = "com.tskhra.grpc.user";

service UserGrpcService {
    rpc GetUserById (GetUserByIdRequest) returns (UserResponse);
    rpc GetUserByKeycloakId (GetUserByKeycloakIdRequest) returns (UserResponse);
    rpc GetUserNameById (GetUserNameRequest) returns (UserNameResponse);
    rpc UserExists (UserExistsRequest) returns (UserExistsResponse);
}

message GetUserByIdRequest {
    int64 user_id = 1;
}

message GetUserByKeycloakIdRequest {
    string keycloak_id = 1;
}

message UserResponse {
    int64 id = 1;
    string keycloak_id = 2;
    string username = 3;
    string first_name = 4;
    string email = 5;
}

message GetUserNameRequest {
    int64 user_id = 1;
}

message UserNameResponse {
    string display_name = 1;
}

message UserExistsRequest {
    string keycloak_id = 1;
}

message UserExistsResponse {
    bool exists = 1;
}
```

```protobuf
// proto/business.proto
syntax = "proto3";
package com.tskhra.business;

option java_multiple_files = true;
option java_package = "com.tskhra.grpc.business";

service BusinessGrpcService {
    rpc GetBusinessById (GetBusinessByIdRequest) returns (BusinessResponse);
    rpc GetServiceById (GetServiceByIdRequest) returns (ServiceResponse);
}

message GetBusinessByIdRequest {
    int64 business_id = 1;
}

message BusinessResponse {
    int64 id = 1;
    string name = 2;
    int64 owner_user_id = 3;
}

message GetServiceByIdRequest {
    int64 service_id = 1;
}

message ServiceResponse {
    int64 id = 1;
    string name = 2;
    int64 business_id = 3;
}
```

#### Maven Dependencies (per service)

```xml
<!-- gRPC dependencies -->
<dependency>
    <groupId>net.devh</groupId>
    <artifactId>grpc-spring-boot-starter</artifactId>
    <version>3.1.0.RELEASE</version>
</dependency>
<dependency>
    <groupId>net.devh</groupId>
    <artifactId>grpc-client-spring-boot-starter</artifactId>
    <version>3.1.0.RELEASE</version>
</dependency>
```

#### gRPC Server (in user-service)

```java
@GrpcService
public class UserGrpcServiceImpl extends UserGrpcServiceGrpc.UserGrpcServiceImplBase {

    private final UserRepository userRepository;

    @Override
    public void getUserByKeycloakId(GetUserByKeycloakIdRequest request,
                                     StreamObserver<UserResponse> responseObserver) {
        User user = userRepository.findByKeycloakId(UUID.fromString(request.getKeycloakId()))
            .orElseThrow(() -> Status.NOT_FOUND
                .withDescription("User not found")
                .asRuntimeException());

        responseObserver.onNext(UserResponse.newBuilder()
            .setId(user.getId())
            .setKeycloakId(user.getKeycloakId().toString())
            .setUsername(user.getUsername())
            .setFirstName(user.getFirstName())
            .setEmail(user.getEmail())
            .build());
        responseObserver.onCompleted();
    }
}
```

#### gRPC Client (in booking-service)

```java
@Component
public class UserGrpcClient {

    @GrpcClient("user-service")
    private UserGrpcServiceGrpc.UserGrpcServiceBlockingStub userStub;

    @CircuitBreaker(name = "userService", fallbackMethod = "getUserFallback")
    public UserResponse getUserByKeycloakId(String keycloakId) {
        return userStub.getUserByKeycloakId(
            GetUserByKeycloakIdRequest.newBuilder()
                .setKeycloakId(keycloakId)
                .build()
        );
    }

    private UserResponse getUserFallback(String keycloakId, Throwable t) {
        // Return cached data or minimal response
        log.warn("User service unavailable, using fallback for {}", keycloakId, t);
        throw new ServiceUnavailableException("User service temporarily unavailable");
    }
}
```

### JWT Claims — Eliminating Most UserService Calls

Your booking_module currently calls `userService.getCurrentUser(jwt)` just to get `id`, `username`, and `keycloakId`. **Add these as Keycloak token claims instead.**

#### Keycloak: Add Custom Protocol Mapper

In Keycloak Admin Console → Realm `tskhra` → Client Scopes → Create mappers:

| Mapper Name | Mapper Type | User Attribute | Token Claim | Claim Type |
|-------------|------------|----------------|-------------|------------|
| user_db_id | User Attribute | user_db_id | user_db_id | long |
| username | User Property | username | preferred_username | String |

The `sub` claim already contains keycloakId. After this, your JWT contains everything booking-service needs for **the current user**.

#### Updated Controller Code (No gRPC Call Needed for Current User)

```java
// Before (requires UserService call):
Long userId = userService.getCurrentUser(jwt).getId();
String username = userService.getCurrentUser(jwt).getUsername();

// After (extracted from JWT directly):
Long userId = jwt.getClaim("user_db_id");
String username = jwt.getClaimAsString("preferred_username");
String keycloakId = jwt.getClaimAsString("sub");
```

#### When You Still Need gRPC

JWT only helps for the **current user's** data. You still need gRPC for:
- `getUserKeycloakIdById(Long userId)` — looking up OTHER users (e.g., business owner for notifications)
- `getUserNameById(Long userId)` — displaying OTHER users' names

These are the only cases where booking-service talks to user-service via gRPC.

### Circuit Breakers (Resilience4j)

```yaml
# application.yml for booking-service
resilience4j:
  circuitbreaker:
    instances:
      userService:
        sliding-window-size: 10
        failure-rate-threshold: 50        # Open circuit after 50% failures
        wait-duration-in-open-state: 10s  # Wait 10s before half-open
        permitted-number-of-calls-in-half-open-state: 3
        slow-call-duration-threshold: 2s
        slow-call-rate-threshold: 80
      businessService:
        sliding-window-size: 10
        failure-rate-threshold: 50
        wait-duration-in-open-state: 10s

  retry:
    instances:
      userService:
        max-attempts: 3
        wait-duration: 500ms
        exponential-backoff-multiplier: 2  # 500ms → 1s → 2s
        retry-exceptions:
          - io.grpc.StatusRuntimeException
        ignore-exceptions:
          - com.tskhra.common.exception.HttpNotFoundException

  timelimiter:
    instances:
      userService:
        timeout-duration: 3s
```

```xml
<!-- Maven dependency -->
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-spring-boot3</artifactId>
    <version>2.2.0</version>
</dependency>
```

### Kafka Event Flow

```
booking-service                              notification-service
     │                                              │
     │  BookingStatusChangedEvent                    │
     ├──────── Kafka: booking.status-changed ───────►│
     │                                              │
     │  BookingCreatedEvent                          │  gRPC: getUserFcmTokens(userId)
     ├──────── Kafka: booking.created ──────────────►├──────► user-service
     │                                              │
     │                                              │  Firebase FCM
     │                                              ├──────► Google FCM API
```

---

## 5. Shared Event Library — JAR via Maven Module (Not Published)

Since you're using a **monorepo**, you don't need to publish JARs to a registry. Maven handles it locally.

### Structure

```
libs/
└── tskhra-events/
    ├── pom.xml
    └── src/main/java/com/tskhra/events/
        ├── booking/
        │   ├── BookingCreatedEvent.java
        │   ├── BookingStatusChangedEvent.java
        │   ├── BookingApprovedEvent.java
        │   ├── BookingRejectedEvent.java
        │   ├── BookingCancelledByUserEvent.java
        │   └── BookingCancelledByBusinessEvent.java
        ├── business/
        │   ├── BusinessRegisteredEvent.java
        │   ├── ServiceCreatedEvent.java
        │   └── ServiceDeactivatedEvent.java
        └── user/
            ├── UserRegisteredEvent.java
            ├── UserProfileUpdatedEvent.java
            └── UserProfilePictureUpdatedEvent.java
```

### pom.xml for tskhra-events

```xml
<project>
    <parent>
        <groupId>com.tskhra</groupId>
        <artifactId>tskhra-parent</artifactId>
        <version>1.0.0</version>
        <relativePath>../../pom.xml</relativePath>
    </parent>

    <artifactId>tskhra-events</artifactId>
    <packaging>jar</packaging>

    <!-- Minimal dependencies — just what events need -->
    <dependencies>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-annotations</artifactId>
        </dependency>
    </dependencies>
</project>
```

### How Services Use It

```xml
<!-- In booking-service/pom.xml -->
<dependency>
    <groupId>com.tskhra</groupId>
    <artifactId>tskhra-events</artifactId>
    <version>${project.version}</version>
</dependency>
```

When you run `mvn clean package` from the root, Maven builds `tskhra-events` first (because it's listed before services in the parent POM's `<modules>`), installs it to local `.m2`, and services pick it up automatically.

### Why Not Publish to a Registry?
- You're solo dev, one repo, one machine. `mvn install` handles everything.
- If you later go polyrepo, then publish to GitHub Packages or a local Nexus.

---

## 6. Common Module — Same Approach, Different Content

### Structure

```
libs/
└── tskhra-common/
    ├── pom.xml
    └── src/main/java/com/tskhra/common/
        ├── exception/
        │   ├── GlobalExceptionHandler.java
        │   ├── HttpBadRequestException.java
        │   ├── HttpNotFoundException.java
        │   ├── HttpUnauthorizedException.java
        │   ├── HttpConflictException.java
        │   ├── HttpForbiddenError.java
        │   ├── HttpException.java
        │   ├── CustomStatusException.java
        │   └── ErrorResponse.java
        ├── validation/
        │   ├── MinAge.java / MinAgeValidator.java
        │   ├── MaxAge.java / MaxAgeValidator.java
        │   ├── ValidPassword.java / PasswordValidator.java
        │   ├── ValidUsername.java / UsernameValidator.java
        │   └── ImageFile.java / ImageFileValidator.java
        └── model/
            └── enums/
                └── MyCustomStatus.java
```

### What Does NOT Go in tskhra-common

| Class | Where It Goes | Why |
|-------|--------------|-----|
| SecurityConfiguration | Each service (copy) | Different public endpoints per service |
| KeycloakConfiguration | user-service only | Only user-service talks to Keycloak admin API |
| MinioConfiguration | user-service, business-service | Only services that handle files |
| SwaggerConfiguration | Each service (copy) | Per-service API docs |
| ImageService | Split into services | User avatars → user-service, business images → business-service |
| Properties classes | Respective services | `SumsubProperties` → user-service, etc. |

### Rule of Thumb
Put something in `tskhra-common` only if **3+ services** need it. If only 1-2 services use it, just copy it — duplication is better than artificial coupling.

---

## 7. Spring Cloud Gateway + Eureka + Nginx for Webhooks

### Spring Cloud Gateway Setup

```xml
<!-- api-gateway/pom.xml -->
<dependencies>
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-gateway</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
    </dependency>
</dependencies>
```

```yaml
# api-gateway application.yml
server:
  port: 8080

spring:
  application:
    name: api-gateway

  cloud:
    gateway:
      discovery:
        locator:
          enabled: true                    # Auto-discover services from Eureka
          lower-case-service-id: true

      routes:
        # User Service
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/v1/users/**, /api/v1/auth/**, /api/v1/credentials/**
          filters:
            - StripPrefix=0

        # KYC Webhook (public — no JWT)
        - id: kyc-webhook
          uri: lb://user-service
          predicates:
            - Path=/kyc/webhook
          filters:
            - StripPrefix=0
          metadata:
            auth-required: false

        # Business Service
        - id: business-service
          uri: lb://business-service
          predicates:
            - Path=/api/v1/businesses/**, /api/v1/services/**, /api/v1/categories/**, /api/v1/cities/**
          filters:
            - StripPrefix=0

        # Booking Service
        - id: booking-service
          uri: lb://booking-service
          predicates:
            - Path=/api/v1/bookings/**
          filters:
            - StripPrefix=0

        # Notification Service
        - id: notification-service
          uri: lb://notification-service
          predicates:
            - Path=/api/v1/notifications/**, /api/v1/fcm/**
          filters:
            - StripPrefix=0

        # WebSocket (messaging)
        - id: messaging-service
          uri: lb:ws://messaging-service
          predicates:
            - Path=/ws/**

  security:
    oauth2:
      resourceserver:
        jwt:
          jwk-set-uri: http://keycloak:8080/realms/tskhra/protocol/openid-connect/certs
```

### Eureka Server (Discovery)

Create a small `discovery-server` service:

```xml
<!-- discovery-server/pom.xml -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-eureka-server</artifactId>
</dependency>
```

```java
@SpringBootApplication
@EnableEurekaServer
public class DiscoveryServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(DiscoveryServerApplication.class, args);
    }
}
```

```yaml
# discovery-server application.yml
server:
  port: 8761

eureka:
  client:
    register-with-eureka: false
    fetch-registry: false
```

Each service registers:
```yaml
# In every service's application.yml
eureka:
  client:
    service-url:
      defaultZone: http://discovery-server:8761/eureka/
  instance:
    prefer-ip-address: true
```

### Nginx for Webhooks + Ngrok

Keep Nginx specifically for the ngrok tunnel scenario. Ngrok exposes one port → Nginx routes to the right service:

```nginx
# nginx.conf — only for external webhook routing via ngrok
server {
    listen 80;

    # Sumsub KYC webhook → api-gateway → user-service
    location /kyc/webhook {
        proxy_pass http://api-gateway:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Future webhooks (e.g., payment provider)
    location /payments/webhook {
        proxy_pass http://api-gateway:8080;
        proxy_set_header Host $host;
    }

    # Everything else (if needed)
    location / {
        proxy_pass http://api-gateway:8080;
    }
}
```

```
ngrok → :80 (nginx) → :8080 (Spring Cloud Gateway) → :808x (actual service)
```

This way ngrok only tunnels port 80, nginx fans out all external callbacks, and Spring Cloud Gateway handles the actual routing + load balancing.

---

## 8. Secrets Management with HashiCorp Vault

### Why Vault?

Your current state is **dangerous**:
- `application.yaml` has hardcoded passwords (`password: password`, `client-secret: hiDfHEHBRbi6VuEPvBDirMecSqINIXit`)
- `.env` file has exposed Sumsub API keys in the repository
- `firebase-service-account.json` is in the repo root

Vault centralizes all secrets and provides:
- Dynamic secret rotation
- Audit logging (who accessed what, when)
- Lease-based access (secrets expire automatically)
- Encryption as a service

### Setup (Docker)

```yaml
# Add to docker-compose.yml
vault:
  image: hashicorp/vault:1.15
  ports:
    - "8200:8200"
  environment:
    VAULT_DEV_ROOT_TOKEN_ID: ${VAULT_TOKEN}  # Only for dev; production uses proper unseal
    VAULT_DEV_LISTEN_ADDRESS: 0.0.0.0:8200
  volumes:
    - vault-data:/vault/data
  cap_add:
    - IPC_LOCK
```

### Store Secrets in Vault

```bash
# Enable KV secrets engine
vault secrets enable -path=secret kv-v2

# Store per-service secrets
vault kv put secret/user-service \
    db.username=user_svc \
    db.password=$(openssl rand -base64 32) \
    keycloak.client-secret=hiDfHEHBRbi6VuEPvBDirMecSqINIXit \
    sumsub.secret-key=DTr7fBGgzTxJLiD79J6fqNzBMRwhiivm \
    sumsub.token=sbx:yPlxcS4RXZpKBm8bq9m5VG3n.Hg7qL21NQtuNbCgctaMYMqAs7tMEdVBK \
    minio.access-key=admin \
    minio.secret-key=$(openssl rand -base64 32)

vault kv put secret/booking-service \
    db.username=booking_svc \
    db.password=$(openssl rand -base64 32)

vault kv put secret/business-service \
    db.username=business_svc \
    db.password=$(openssl rand -base64 32) \
    minio.access-key=admin \
    minio.secret-key=$(openssl rand -base64 32)

vault kv put secret/application \
    redis.password=$(openssl rand -base64 32) \
    kafka.password=changeme
```

### Spring Cloud Vault Integration

```xml
<!-- Add to each service -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-vault-config</artifactId>
</dependency>
```

```yaml
# bootstrap.yml (loaded before application.yml)
spring:
  cloud:
    vault:
      host: vault
      port: 8200
      scheme: http
      authentication: TOKEN       # Use APPROLE in production
      token: ${VAULT_TOKEN}
      kv:
        enabled: true
        backend: secret
        application-name: ${spring.application.name}
```

Now your `application.yml` becomes:
```yaml
# Before (INSECURE):
spring:
  datasource:
    username: tskhra_admin
    password: password

# After (secrets injected from Vault):
spring:
  datasource:
    username: ${db.username}
    password: ${db.password}
```

### Simpler Alternative: Docker Secrets + Environment Variables

If Vault feels overkill for a solo dev, use Docker secrets:

```yaml
# docker-compose.yml
services:
  user-service:
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt  # NOT in git (.gitignore it)
```

**Minimum action items right now:**
1. Add `*.json` credential files to `.gitignore`
2. Move ALL secrets to environment variables
3. Never commit `.env` — add it to `.gitignore` and use `.env.example` with placeholders
4. Consider Vault when you're ready for production

---

## 9. Observability Guide

### The Three Pillars

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Logs      │     │   Metrics    │     │   Traces     │
│  (ELK Stack) │     │ (Prometheus  │     │  (Zipkin /   │
│              │     │  + Grafana)  │     │   Jaeger)    │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │    What happened?  │  How is it doing?  │  Where did it go?
       │    Error logs,     │  CPU, memory,      │  Request flow across
       │    audit trail     │  request rate,     │  services, latency
       │                    │  error rate        │  per hop
       └────────────────────┴────────────────────┘
```

### Pillar 1: ELK Stack (Logs)

You already have Elasticsearch + Kibana. Add structured logging:

```xml
<!-- Each service pom.xml -->
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>7.4</version>
</dependency>
```

```xml
<!-- logback-spring.xml in each service -->
<configuration>
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <includeMdcKeyName>traceId</includeMdcKeyName>
            <includeMdcKeyName>spanId</includeMdcKeyName>
            <customFields>{"service":"${SERVICE_NAME}"}</customFields>
        </encoder>
    </appender>

    <!-- Send to Logstash (optional — or use Filebeat) -->
    <appender name="LOGSTASH" class="net.logstash.logback.appender.LogstashTcpSocketAppender">
        <destination>logstash:5044</destination>
        <encoder class="net.logstash.logback.encoder.LogstashEncoder"/>
    </appender>

    <root level="INFO">
        <appender-ref ref="STDOUT"/>
        <appender-ref ref="LOGSTASH"/>
    </root>
</configuration>
```

Add Logstash to docker-compose:
```yaml
logstash:
  image: docker.elastic.co/logstash/logstash:8.13.0
  volumes:
    - ./infra/logstash/pipeline:/usr/share/logstash/pipeline
  depends_on:
    - elasticsearch
```

### Pillar 2: Prometheus + Grafana (Metrics)

```xml
<!-- Each service pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

```yaml
# Each service application.yml
management:
  endpoints:
    web:
      exposure:
        include: health, prometheus, info, metrics
  endpoint:
    health:
      show-details: always
  metrics:
    tags:
      application: ${spring.application.name}
```

```yaml
# docker-compose.yml additions
prometheus:
  image: prom/prometheus:v2.51.0
  ports:
    - "9090:9090"
  volumes:
    - ./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana:10.4.0
  ports:
    - "3000:3000"
  environment:
    GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
  volumes:
    - grafana-data:/var/lib/grafana
```

```yaml
# infra/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'user-service'
    metrics_path: /actuator/prometheus
    static_configs:
      - targets: ['user-service:8081']

  - job_name: 'booking-service'
    metrics_path: /actuator/prometheus
    static_configs:
      - targets: ['booking-service:8082']

  - job_name: 'business-service'
    metrics_path: /actuator/prometheus
    static_configs:
      - targets: ['business-service:8083']

  - job_name: 'notification-service'
    metrics_path: /actuator/prometheus
    static_configs:
      - targets: ['notification-service:8084']

  - job_name: 'api-gateway'
    metrics_path: /actuator/prometheus
    static_configs:
      - targets: ['api-gateway:8080']
```

**Key Grafana dashboards to set up:**
- JVM dashboard (heap, GC, threads) — import dashboard ID `4701`
- Spring Boot dashboard — import dashboard ID `12900`
- Resilience4j circuit breaker dashboard

### Pillar 3: Zipkin (Distributed Tracing)

```xml
<!-- Each service pom.xml -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-brave</artifactId>
</dependency>
<dependency>
    <groupId>io.zipkin.reporter2</groupId>
    <artifactId>zipkin-reporter-brave</artifactId>
</dependency>
```

```yaml
# Each service application.yml
management:
  tracing:
    sampling:
      probability: 1.0   # 100% in dev, lower in prod (0.1 = 10%)
  zipkin:
    tracing:
      endpoint: http://zipkin:9411/api/v2/spans
```

```yaml
# docker-compose.yml
zipkin:
  image: openzipkin/zipkin:3
  ports:
    - "9411:9411"
```

**What tracing gives you**: When a user creates a booking, you see:
```
[api-gateway: 5ms] → [booking-service: 45ms] → [user-service (gRPC): 12ms]
                                               → [kafka publish: 3ms]
                                                    → [notification-service: 120ms]
                                                         → [Firebase FCM: 95ms]
```

### RAM Impact on Your 16GB Laptop

| Component | Additional RAM |
|-----------|---------------|
| Prometheus | ~200MB |
| Grafana | ~150MB |
| Zipkin | ~200MB |
| Logstash | ~500MB |
| **Total** | **~1GB** |

You already have Elasticsearch + Kibana (~2-3GB). Total observability stack: ~3-4GB. That's tight on 16GB. **Compromise**: Skip Logstash and use direct Elasticsearch output from logback, saving ~500MB.

---

## 10. Testing Guide

### Unit Tests

Unit tests mock all dependencies and test one class in isolation. Fast, no Spring context.

#### Service Layer Example

```java
@ExtendWith(MockitoExtension.class)
class BookingServiceTest {

    @Mock private BookingRepository bookingRepository;
    @Mock private UserGrpcClient userGrpcClient;
    @Mock private ApplicationEventPublisher eventPublisher;
    @InjectMocks private BookingService bookingService;

    @Test
    void createBooking_shouldSaveAndPublishEvent() {
        // Given
        BookingRequest request = BookingRequest.builder()
            .serviceId(1L)
            .date(LocalDate.of(2026, 5, 1))
            .time(LocalTime.of(10, 0))
            .build();

        Booking savedBooking = Booking.builder()
            .id(1L)
            .userId(42L)
            .status(BookingStatus.PENDING)
            .build();

        when(bookingRepository.save(any(Booking.class))).thenReturn(savedBooking);

        // When
        BookingDto result = bookingService.createBooking(request, 42L);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getStatus()).isEqualTo(BookingStatus.PENDING);
        verify(bookingRepository).save(any(Booking.class));
        verify(eventPublisher).publishEvent(any(BookingStatusChangedEvent.class));
    }

    @Test
    void createBooking_whenUserNotFound_shouldThrow() {
        // Given
        when(userGrpcClient.getUserByKeycloakId(anyString()))
            .thenThrow(new ServiceUnavailableException("User service down"));

        // When/Then
        assertThatThrownBy(() -> bookingService.createBooking(request, "bad-id"))
            .isInstanceOf(ServiceUnavailableException.class);
    }

    @Test
    void approveBooking_whenNotOwner_shouldThrowForbidden() {
        // Given
        Booking booking = Booking.builder()
            .id(1L)
            .status(BookingStatus.PENDING)
            .build();

        when(bookingRepository.findById(1L)).thenReturn(Optional.of(booking));

        // When/Then — user 99 is not the business owner
        assertThatThrownBy(() -> bookingService.approveRequest(1L, 99L))
            .isInstanceOf(HttpForbiddenError.class);
    }
}
```

#### Controller Layer Example

```java
@WebMvcTest(BookingController.class)
@Import(SecurityConfiguration.class)
class BookingControllerTest {

    @Autowired private MockMvc mockMvc;
    @MockBean private BookingService bookingService;

    @Test
    @WithMockJwt(sub = "keycloak-uuid-123", claims = {"user_db_id=42"})
    void createBooking_shouldReturn201() throws Exception {
        BookingDto response = BookingDto.builder()
            .id(1L)
            .status(BookingStatus.PENDING)
            .build();

        when(bookingService.createBooking(any(), eq(42L))).thenReturn(response);

        mockMvc.perform(post("/api/v1/bookings")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                        "serviceId": 1,
                        "date": "2026-05-01",
                        "time": "10:00"
                    }
                    """))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.status").value("PENDING"));
    }

    @Test
    void createBooking_withoutAuth_shouldReturn401() throws Exception {
        mockMvc.perform(post("/api/v1/bookings")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{}"))
                .andExpect(status().isUnauthorized());
    }
}
```

#### What to Unit Test

| Layer | What to Test | What NOT to Test |
|-------|-------------|-----------------|
| Service | Business logic, validation, edge cases | Database queries, framework behavior |
| Controller | Request/response mapping, auth, validation | Service logic (mocked) |
| Validators | Valid/invalid inputs, boundary values | — |
| Event listeners | Event handling logic | Kafka delivery |
| gRPC clients | Fallback behavior, error mapping | Network layer |

### Integration Tests in Microservices

#### Per-Service Integration Tests (Testcontainers)

Test one service with real infrastructure (DB, Kafka, Redis) but mock other services:

```xml
<!-- Test dependencies -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>kafka</artifactId>
    <scope>test</scope>
</dependency>
```

```java
@SpringBootTest
@Testcontainers
class BookingServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
        .withDatabaseName("tskhra_bookings_test");

    @Container
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:7.6.0"));

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }

    @MockBean
    private UserGrpcClient userGrpcClient;  // Mock other services

    @Autowired
    private BookingService bookingService;

    @Autowired
    private BookingRepository bookingRepository;

    @Test
    void createBooking_shouldPersistAndPublishEvent() {
        // Given — mock the gRPC call to user-service
        when(userGrpcClient.getUserByKeycloakId("kc-123"))
            .thenReturn(UserResponse.newBuilder()
                .setId(42L)
                .setUsername("testuser")
                .build());

        // When
        BookingDto result = bookingService.createBooking(request, 42L);

        // Then — verify it's in the database
        Optional<Booking> saved = bookingRepository.findById(result.getId());
        assertThat(saved).isPresent();
        assertThat(saved.get().getStatus()).isEqualTo(BookingStatus.PENDING);

        // Verify Kafka event was published (use embedded Kafka consumer)
    }
}
```

#### Contract Tests (Spring Cloud Contract)

Prevent breaking changes between services. The **provider** defines contracts, the **consumer** verifies them:

```java
// In user-service (provider) — contract test
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.MOCK)
@AutoConfigureStubRunner
class UserServiceContractTest {

    @Test
    void shouldReturnUserForValidKeycloakId() {
        // This test is auto-generated from contract DSL
        // Ensures user-service always returns the expected response shape
    }
}
```

```groovy
// Contract DSL (user-service/src/test/resources/contracts/)
Contract.make {
    description "should return user by keycloak ID"
    request {
        method GET()
        url "/internal/users/by-keycloak-id/550e8400-e29b-41d4-a716-446655440000"
    }
    response {
        status 200
        body([
            id: 42,
            keycloakId: "550e8400-e29b-41d4-a716-446655440000",
            username: "testuser",
            firstName: "Test"
        ])
        headers {
            contentType(applicationJson())
        }
    }
}
```

#### End-to-End Tests

Run the full stack (docker-compose) and test user journeys:

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.NONE)
class BookingE2ETest {

    // Hit the API gateway, not individual services
    private final WebClient client = WebClient.create("http://localhost:8080");

    @Test
    void fullBookingFlow() {
        // 1. Register user (or get test JWT from Keycloak)
        String jwt = getTestToken();

        // 2. Create a business
        BusinessDto business = client.post()
            .uri("/api/v1/businesses")
            .header("Authorization", "Bearer " + jwt)
            .bodyValue(businessRequest)
            .retrieve()
            .bodyToMono(BusinessDto.class)
            .block();

        // 3. Create a booking
        BookingDto booking = client.post()
            .uri("/api/v1/bookings")
            .header("Authorization", "Bearer " + jwt)
            .bodyValue(bookingRequest)
            .retrieve()
            .bodyToMono(BookingDto.class)
            .block();

        assertThat(booking.getStatus()).isEqualTo("PENDING");

        // 4. Verify notification was sent (check FCM mock or logs)
    }
}
```

### Testing Pyramid for Your Project

```
        /\
       /  \     E2E Tests (5-10 tests)
      / E2E\    Full stack via docker-compose
     /──────\   Slow, run on CI only
    /Contract\  Contract Tests (per service pair)
   /──────────\ Prevent breaking API changes
  /Integration \ Integration Tests (per service)
 /──────────────\ Real DB + Kafka via Testcontainers
/ Unit Tests     \ Unit Tests (bulk of tests)
/──────────────────\ Fast, no Spring context, Mockito
```

**Start here**: Write unit tests for all service classes. You currently have tests only for `UserService` and validators. Add tests for `BookingService`, `BusinessService`, `ServiceService` before migration.

---

## Bonus: Swagger in Microservices

### Problem
Each service has its own Swagger UI at `/swagger-ui.html`. Users don't want to visit 5 different URLs.

### Solution: Aggregated Swagger via API Gateway

```xml
<!-- api-gateway pom.xml -->
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webflux-ui</artifactId>
    <version>3.0.1</version>
</dependency>
```

```yaml
# api-gateway application.yml
springdoc:
  swagger-ui:
    urls:
      - name: User Service
        url: /v3/api-docs/user-service
      - name: Business Service
        url: /v3/api-docs/business-service
      - name: Booking Service
        url: /v3/api-docs/booking-service
      - name: Notification Service
        url: /v3/api-docs/notification-service

  # Route API doc requests to each service
  api-docs:
    enabled: true

spring:
  cloud:
    gateway:
      routes:
        # API docs routing
        - id: user-service-docs
          uri: lb://user-service
          predicates:
            - Path=/v3/api-docs/user-service
          filters:
            - RewritePath=/v3/api-docs/user-service, /v3/api-docs

        - id: business-service-docs
          uri: lb://business-service
          predicates:
            - Path=/v3/api-docs/business-service
          filters:
            - RewritePath=/v3/api-docs/business-service, /v3/api-docs

        - id: booking-service-docs
          uri: lb://booking-service
          predicates:
            - Path=/v3/api-docs/booking-service
          filters:
            - RewritePath=/v3/api-docs/booking-service, /v3/api-docs

        - id: notification-service-docs
          uri: lb://notification-service
          predicates:
            - Path=/v3/api-docs/notification-service
          filters:
            - RewritePath=/v3/api-docs/notification-service, /v3/api-docs
```

### Per-Service Swagger Config

Each service still has its own `SwaggerConfiguration`:

```java
@Configuration
public class SwaggerConfiguration {

    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("Booking Service API")
                .version("v1")
                .description("Booking management endpoints"))
            .addSecurityItem(new SecurityRequirement().addList("Bearer"))
            .components(new Components()
                .addSecuritySchemes("Bearer",
                    new SecurityScheme()
                        .type(SecurityScheme.Type.HTTP)
                        .scheme("bearer")
                        .bearerFormat("JWT")));
    }
}
```

### Result

Single Swagger UI at `http://api-gateway:8080/swagger-ui.html` with a dropdown to switch between services:
```
┌─────────────────────────────────────────┐
│  Swagger UI          [User Service  ▼]  │
│                       User Service      │
│  GET  /api/v1/users   Business Service  │
│  POST /api/v1/users   Booking Service   │
│  ...                  Notification Svc  │
└─────────────────────────────────────────┘
```