package com.tskhra.modulith.user_module.controllers;

import com.tskhra.modulith.user_module.model.requests.*;
import com.tskhra.modulith.user_module.model.responses.ChallengeResponse;
import com.tskhra.modulith.user_module.model.responses.MessageResponse;
import io.swagger.v3.oas.annotations.Operation;
import com.tskhra.modulith.user_module.model.responses.TokensResponse;
import com.tskhra.modulith.user_module.services.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @Operation(summary = "Authenticate and obtain tokens")
    @PostMapping("/login")
    public ResponseEntity<TokensResponse> login(@RequestBody LoginRequestDto dto) {
        TokensResponse tokens = authService.login(dto);
        return ResponseEntity.ok(tokens);
    }

    @Operation(summary = "Refresh access token")
    @PostMapping("/refresh")
    public ResponseEntity<TokensResponse> refresh(@RequestBody RefreshTokenRequest dto) {
        TokensResponse token = authService.refreshToken(dto);
        return ResponseEntity.ok(token);
    }

    @PostMapping("/biometric/register")
    public ResponseEntity<MessageResponse> registerDevice(@AuthenticationPrincipal Jwt jwt,
                                                          @Valid @RequestBody BiometricsDto biometrics) {

        authService.registerDevice(biometrics, jwt);
        MessageResponse body = new MessageResponse(
                HttpStatus.OK.value(),
                "Device registered successfully",
                Instant.now().toString()
        );
        return ResponseEntity.ok(body);
    }

    @PostMapping("/biometric/challenge")
    public ResponseEntity<ChallengeResponse> generateChallenge(@RequestBody ChallengeRequest request) {

        String challenge = authService.generateChallenge(request);
        ChallengeResponse body = new ChallengeResponse(
                HttpStatus.OK.value(),
                "Challenge generated successfully",
                Instant.now().toString(),
                challenge
        );
        return ResponseEntity.ok(body);
    }

    @PostMapping("/biometric/verify")
    public ResponseEntity<TokensResponse> verifyBiometrics(@RequestBody VerifyRequest request) {
        TokensResponse tokens = authService.verifyAndLogin(request);
        return ResponseEntity.ok(tokens);
    }

    @Operation(summary = "Logout and invalidate tokens")
    @PostMapping("/logout")
    public ResponseEntity<MessageResponse> logout(@RequestBody RefreshTokenRequest dto) {
        authService.logout(dto);
        MessageResponse body = new MessageResponse(
                HttpStatus.OK.value(),
                "Logged out successfully",
                Instant.now().toString()
        );
        return ResponseEntity.ok(body);
    }

    @Operation(summary = "Unregister biometric device")
    @PostMapping("/biometric/unregister")
    public ResponseEntity<MessageResponse> unregisterDevice(@AuthenticationPrincipal Jwt jwt,
                                                             @RequestBody ChallengeRequest request) {
        authService.unregisterDevice(request.deviceId(), jwt);
        MessageResponse body = new MessageResponse(
                HttpStatus.OK.value(),
                "Device unregistered successfully",
                Instant.now().toString()
        );
        return ResponseEntity.ok(body);
    }

}
