package com.tskhra.modulith.user_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.common.properties.KeycloakProperties;
import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpUnauthorizedException;
import com.tskhra.modulith.user_module.model.domain.UserBiometricDevices;
import com.tskhra.modulith.user_module.model.requests.*;
import com.tskhra.modulith.user_module.model.responses.TokensResponse;
import com.tskhra.modulith.user_module.repositories.UserBiometricDevicesRepository;

import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;

import java.security.KeyFactory;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.X509EncodedKeySpec;
import java.time.Duration;
import java.util.Base64;
import java.util.UUID;
import java.util.function.Predicate;

@Service
@Slf4j
public class AuthService {

    private final KeycloakProperties keycloakProperties;
    private final RestClient restClient;
    private final StringRedisTemplate redisTemplate;

    private final UserBiometricDevicesRepository userBiometricDevicesRepository;

    public AuthService(KeycloakProperties keycloakProperties, RestClient.Builder restClientBuilder, UserBiometricDevicesRepository userBiometricDevicesRepository, StringRedisTemplate redisTemplate) {
        this.keycloakProperties = keycloakProperties;

        String tokenUrl = String.format("%s/realms/%s/protocol/openid-connect/token",
                keycloakProperties.serverUrl(), keycloakProperties.realm());

        this.restClient = restClientBuilder
                .baseUrl(tokenUrl)
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_FORM_URLENCODED_VALUE)
                .build();

        this.userBiometricDevicesRepository = userBiometricDevicesRepository;
        this.redisTemplate = redisTemplate;
    }

    public TokensResponse login(LoginRequestDto dto) {
        MultiValueMap<String, String> formData = new LinkedMultiValueMap<>();
        formData.add("client_id", keycloakProperties.clientId());
        formData.add("client_secret", keycloakProperties.clientSecret());
        formData.add("grant_type", "password");
        formData.add("username", dto.username());
        formData.add("password", dto.password());

        return restClient.post()
                .body(formData)
                .retrieve()
                .onStatus(_401, throw401)
                .body(TokensResponse.class);
    }

    public TokensResponse refreshToken(RefreshTokenRequest dto) {
        MultiValueMap<String, String> formData = new LinkedMultiValueMap<>();
        formData.add("grant_type", "refresh_token");
        formData.add("client_id", keycloakProperties.clientId());
        formData.add("client_secret", keycloakProperties.clientSecret());
        formData.add("refresh_token", dto.refreshToken());

        return restClient.post()
                .body(formData)
                .retrieve()
                .onStatus(_400, throw400)
                .body(TokensResponse.class);
    }

    private static final Predicate<HttpStatusCode> _400 = code -> code.value() == 400;
    private static final Predicate<HttpStatusCode> _401 = code -> code.value() == 401;

    private static final RestClient.ResponseSpec.ErrorHandler throw400 = (req, resp) -> {
        throw new HttpBadRequestException("Invalid refresh token.");
    };

    private static final RestClient.ResponseSpec.ErrorHandler throw401 = (req, resp) -> {
        throw new HttpUnauthorizedException("Invalid credentials.");
    };

    @Transactional
    public void registerDevice(BiometricsDto biometrics, Jwt jwt) {
        log.info("Registering device: {}", biometrics);
        String userKeycloakId = jwt.getClaimAsString("sub");

        UserBiometricDevices device = userBiometricDevicesRepository.findByDeviceId(biometrics.deviceId())
                .orElse(new UserBiometricDevices());

        device.setUserId(userKeycloakId);
        device.setDeviceId(biometrics.deviceId());
        device.setPublicKey(biometrics.publicKey());
        UserBiometricDevices saved = userBiometricDevicesRepository.save(device);
        log.info("Device registered with id: {}", saved.getId());
    }

    public String generateChallenge(ChallengeRequest request) {
        log.info("Generating challenge for device: {}", request.deviceId());
        String deviceId = request.deviceId();

        boolean deviceExists = userBiometricDevicesRepository.findByDeviceId(deviceId).isPresent();
        if (!deviceExists) {
            log.error("Device not registered: {}", deviceId);
            throw new HttpNotFoundException("Device not registered.");
        }

        String challenge = UUID.randomUUID().toString();
        String redisKey = "biometric_nonce:" + deviceId;

        redisTemplate.opsForValue().set(redisKey, challenge, Duration.ofSeconds(600)); // todo CHANGE to 60sec!
        log.info("Challenge generated for device: {}", deviceId);
        return challenge;
    }

    public TokensResponse verifyAndLogin(VerifyRequest request) {
        log.info("Verifying device: {}", request.deviceId());
        String redisKey = "biometric_nonce:" + request.deviceId();
        String challenge = redisTemplate.opsForValue().getAndDelete(redisKey);
        log.info("Challenge retrieved for device: {}", request.deviceId());

        if (challenge == null) {
            log.error("Challenge expired or invalid for device: {}", request.deviceId());
            throw new HttpUnauthorizedException("Challenge expired or invalid.");
        }

        UserBiometricDevices device = userBiometricDevicesRepository.findByDeviceId(request.deviceId())
                .orElseThrow(() -> new HttpUnauthorizedException("Device not registered."));

        boolean isValidSignature = verifySignature(device.getPublicKey(), challenge, request.signature());
        if (!isValidSignature) {
            log.error("Invalid signature for device: {}", request.deviceId());
            throw new HttpUnauthorizedException("Invalid signature.");
        }

        return exchangeTokenForUser(device.getUserId());
    }


    public TokensResponse exchangeTokenForUser(String userId) {

        MultiValueMap<String, String> serviceAccountForm = new LinkedMultiValueMap<>();
        serviceAccountForm.add("client_id", keycloakProperties.clientId());
        serviceAccountForm.add("client_secret", keycloakProperties.clientSecret());
        serviceAccountForm.add("grant_type", "client_credentials");

        TokensResponse serviceToken = restClient.post()
                .body(serviceAccountForm)
                .retrieve()
                .onStatus(_401, throw401)
                .body(TokensResponse.class);

        // Step 2: Exchange service account token for user token
        MultiValueMap<String, String> exchangeForm = new LinkedMultiValueMap<>();
        exchangeForm.add("client_id", keycloakProperties.clientId());
        exchangeForm.add("client_secret", keycloakProperties.clientSecret());
        exchangeForm.add("grant_type", "urn:ietf:params:oauth:grant-type:token-exchange");
        exchangeForm.add("subject_token", serviceToken.accessToken());
        exchangeForm.add("requested_token_type", "urn:ietf:params:oauth:token-type:refresh_token");
        exchangeForm.add("requested_subject", userId);

        return restClient.post()
                .body(exchangeForm)
                .retrieve()
                .onStatus(_400, (req, resp) -> {
                    throw new HttpBadRequestException("Token exchange failed.");
                })
                .onStatus(_401, throw401)
                .body(TokensResponse.class);
    }

    public void logout(RefreshTokenRequest dto) {
        String logoutUrl = String.format("%s/realms/%s/protocol/openid-connect/logout",
                keycloakProperties.serverUrl(), keycloakProperties.realm());

        MultiValueMap<String, String> formData = new LinkedMultiValueMap<>();
        formData.add("client_id", keycloakProperties.clientId());
        formData.add("client_secret", keycloakProperties.clientSecret());
        formData.add("refresh_token", dto.refreshToken());

        RestClient.create().post()
                .uri(logoutUrl)
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                .body(formData)
                .retrieve()
                .onStatus(_400, (req, resp) -> {
                    throw new HttpBadRequestException("Logout failed: invalid token.");
                })
                .toBodilessEntity();

        log.info("User session invalidated successfully.");
    }

    @Transactional
    public void unregisterDevice(String deviceId, Jwt jwt) {
        String userId = jwt.getClaimAsString("sub");

        UserBiometricDevices device = userBiometricDevicesRepository.findByDeviceId(deviceId)
                .orElseThrow(() -> new HttpNotFoundException("Device not found."));

        if (!device.getUserId().equals(userId)) {
            throw new HttpUnauthorizedException("Device does not belong to this user.");
        }

        userBiometricDevicesRepository.delete(device);
        log.info("Device {} unregistered for user {}", deviceId, userId);
    }

    private boolean verifySignature(String publicKey, String challenge, String signature) {
        try {
            String cleanKey = publicKey
                    .replace("-----BEGIN PUBLIC KEY-----", "")
                    .replace("-----END PUBLIC KEY-----", "")
                    .replaceAll("\\s+", "");

            byte[] pubKeyBytes = Base64.getDecoder().decode(cleanKey);
            X509EncodedKeySpec spec = new X509EncodedKeySpec(pubKeyBytes);

            PublicKey pubKey = decodePublicKey(spec);

            String algorithm = switch (pubKey.getAlgorithm()) {
                case "RSA" -> "SHA256withRSA";
                case "EC" -> "SHA256withECDSA";
                default -> throw new IllegalArgumentException(
                        "Unsupported key algorithm: " + pubKey.getAlgorithm());
            };

            byte[] signatureBytes = Base64.getDecoder().decode(signature);
            Signature sig = Signature.getInstance(algorithm);
            sig.initVerify(pubKey);
            sig.update(challenge.getBytes());

            boolean verify = sig.verify(signatureBytes);
            log.info("Signature verification result: {}", verify);
            return verify;

        } catch (Exception e) {
            log.error("Error verifying signature: {}", e.getMessage());
            return false;
        }
    }

    private PublicKey decodePublicKey(X509EncodedKeySpec spec) throws InvalidKeySpecException, NoSuchAlgorithmException {
        try {
            return KeyFactory.getInstance("RSA").generatePublic(spec);
        } catch (InvalidKeySpecException e) {
            return KeyFactory.getInstance("EC").generatePublic(spec);
        }
    }
}
