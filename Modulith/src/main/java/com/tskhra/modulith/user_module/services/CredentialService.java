package com.tskhra.modulith.user_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpConflictException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpUnauthorizedException;
import com.tskhra.modulith.user_module.model.domain.UserDevice;
import com.tskhra.modulith.user_module.model.enums.CredentialType;
import com.tskhra.modulith.user_module.model.requests.ChallengeRequest;
import com.tskhra.modulith.user_module.model.requests.CredentialUpdateRequest;
import com.tskhra.modulith.user_module.model.requests.CredentialsRegisterRequest;
import com.tskhra.modulith.user_module.model.requests.VerifyRequest;
import com.tskhra.modulith.user_module.model.responses.TokensResponse;
import com.tskhra.modulith.user_module.repositories.UserDevicesRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.KeyFactory;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.X509EncodedKeySpec;
import java.time.Duration;
import java.util.Base64;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class CredentialService {

    private final AuthService authService;
    private final UserDevicesRepository userDevicesRepository;
    private final StringRedisTemplate redisTemplate;

    @Transactional
    public void registerDevice(CredentialsRegisterRequest request, Jwt jwt) {
        String userKeycloakId = jwt.getSubject();
        String deviceId = request.deviceId();

        boolean deviceExists = userDevicesRepository.existsUserDeviceByDeviceId(deviceId);
        if (deviceExists) {
            throw new HttpConflictException("Device with same id is already registered.");
        }

        Map<CredentialType, String> credentials = request.credentials();
        String pinPublicKey = credentials.getOrDefault(CredentialType.PIN, null);
        String bioPublicKey = credentials.getOrDefault(CredentialType.BIO, null);

        UserDevice device = UserDevice.builder()
                .userId(userKeycloakId)
                .deviceId(deviceId)
                .pinPublicKey(pinPublicKey)
                .biometricPublicKey(bioPublicKey)
                .build();

        userDevicesRepository.save(device);
    }

    @Transactional
    public String generateChallenge(ChallengeRequest challengeRequest) {
        String deviceId = challengeRequest.deviceId();

        boolean deviceExists = userDevicesRepository.existsUserDeviceByDeviceId(deviceId);
        if (!deviceExists) {
            throw new HttpNotFoundException("Device not registered.");
        }

        String challenge = UUID.randomUUID().toString();
        String redisKey = "biometric_nonce:" + deviceId;

        redisTemplate.opsForValue().set(redisKey, challenge, Duration.ofSeconds(600)); // todo CHANGE to 60sec!
        return challenge;
    }

    @Transactional
    public TokensResponse verifyAndLogin(VerifyRequest request, CredentialType type) {
        String redisKey = "biometric_nonce:" + request.deviceId();
        String challenge = redisTemplate.opsForValue().getAndDelete(redisKey);

        if (challenge == null) {
            throw new HttpUnauthorizedException("Challenge expired or invalid.");
        }

        UserDevice device = userDevicesRepository.findByDeviceId(request.deviceId())
                .orElseThrow(() -> new HttpUnauthorizedException("Device not registered."));

        String publicKey = switch (type) {
            case PIN -> device.getPinPublicKey();
            case BIO -> device.getBiometricPublicKey();
        };

        boolean isValidSignature = verifySignature(publicKey, challenge, request.signature());
        if (!isValidSignature) {
            throw new HttpUnauthorizedException("Invalid signature.");
        }

        return authService.exchangeTokenForUser(device.getUserId());
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
            return verify;

        } catch (Exception e) {
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


    @Transactional
    public void updatePublicKey(CredentialUpdateRequest credentialUpdateRequest, CredentialType type) {
        String deviceId = credentialUpdateRequest.deviceId();
        String publicKey = credentialUpdateRequest.publicKey();

        UserDevice device = userDevicesRepository.findByDeviceId(deviceId)
                .orElseThrow(() -> new HttpUnauthorizedException("Device not registered."));

        switch (type) {
            case PIN -> device.setPinPublicKey(publicKey);
            case BIO -> device.setBiometricPublicKey(publicKey);
        }

        userDevicesRepository.save(device);
    }
}
