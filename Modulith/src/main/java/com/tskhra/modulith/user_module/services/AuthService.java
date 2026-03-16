package com.tskhra.modulith.user_module.services;

import com.tskhra.modulith.common.properties.KeycloakProperties;
import com.tskhra.modulith.common.exception.HttpBadRequestException;
import com.tskhra.modulith.common.exception.HttpUnauthorizedException;
import com.tskhra.modulith.user_module.model.domain.UserBiometricDevices;
import com.tskhra.modulith.user_module.model.requests.*;
import com.tskhra.modulith.user_module.model.responses.ChallengeResponse;
import com.tskhra.modulith.user_module.model.responses.TokensResponse;
import com.tskhra.modulith.user_module.repositories.UserBiometricDevicesRepository;
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
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.X509EncodedKeySpec;
import java.time.Duration;
import java.util.Base64;
import java.util.UUID;
import java.util.function.Predicate;

@Service
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
        String userKeycloakId = jwt.getClaimAsString("sub");

        UserBiometricDevices device = userBiometricDevicesRepository.findByDeviceId(biometrics.deviceId())
                .orElse(new UserBiometricDevices());

        device.setUserId(userKeycloakId);
        device.setDeviceId(biometrics.deviceId());
        device.setPublicKey(biometrics.publicKey());

        userBiometricDevicesRepository.save(device);
    }

    public ChallengeResponse generateChallenge(ChallengeRequest request) {
        String deviceId = request.deviceId();

        String challenge = UUID.randomUUID().toString();
        String redisKey = "biometric_nonce:" + deviceId;

        redisTemplate.opsForValue().set(redisKey, challenge, Duration.ofSeconds(60));
        return new ChallengeResponse(challenge);
    }

    public TokensResponse verifyAndLogin(VerifyRequest request) {
        String redisKey = "biometric_nonce:" + request.deviceId();
        String challenge = redisTemplate.opsForValue().getAndDelete(redisKey);

        if (challenge == null) {
            throw new HttpUnauthorizedException("Challenge expired or invalid.");
        }

        UserBiometricDevices device = userBiometricDevicesRepository.findByDeviceId(request.deviceId())
                .orElseThrow(() -> new HttpUnauthorizedException("Device not registered."));

        boolean isValidSignature = verifySignature(device.getPublicKey(), challenge, request.signature());
        if (!isValidSignature) {
            throw new HttpUnauthorizedException("Invalid signature.");
        }

        return refreshToken(new RefreshTokenRequest(request.refreshToken()));
    }

    private boolean verifySignature(String publicKey, String challenge, String signature) { // todo ???
        // signature is challenge signed with private key and then encoded base 64
        // publicKey is also base64 encoded
        try {
            String cleanKey = publicKey
                    .replace("-----BEGIN PUBLIC KEY-----", "")
                    .replace("-----END PUBLIC KEY-----", "")
                    .replaceAll("\\s+", "");

            byte[] keyBytes = Base64.getDecoder().decode(cleanKey);
            X509EncodedKeySpec spec = new X509EncodedKeySpec(keyBytes);
            PublicKey pubKey = KeyFactory.getInstance("RSA").generatePublic(spec);

            Signature publicSignature = Signature.getInstance("SHA256withRSA");
            publicSignature.initVerify(pubKey);
            publicSignature.update(challenge.getBytes("UTF-8"));

            byte[] signatureBytes = Base64.getDecoder().decode(signature);
            return publicSignature.verify(signatureBytes);
        } catch (Exception e) {
            return false;
        }
    }
}
