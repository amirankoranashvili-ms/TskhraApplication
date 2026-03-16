package com.tskhra.modulith.user_module.controllers;

import com.tskhra.modulith.user_module.model.requests.BiometricsDto;
import com.tskhra.modulith.user_module.model.requests.ChallengeRequest;
import com.tskhra.modulith.user_module.model.requests.LoginRequestDto;
import com.tskhra.modulith.user_module.model.responses.ChallengeResponse;
import io.swagger.v3.oas.annotations.Operation;
import com.tskhra.modulith.user_module.model.requests.RefreshTokenRequest;
import com.tskhra.modulith.user_module.model.responses.TokensResponse;
import com.tskhra.modulith.user_module.services.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

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
    public ResponseEntity<Void> registerDevice(@AuthenticationPrincipal Jwt jwt,
                                               @RequestBody BiometricsDto biometrics) {

        authService.registerDevice(biometrics, jwt);
        return new ResponseEntity<>(HttpStatus.OK);
    }

    @PostMapping("/biometric/challenge")
    public ResponseEntity<ChallengeResponse> generateChallenge(@RequestBody ChallengeRequest request) {

        ChallengeResponse response = authService.generateChallenge(request);
        return ResponseEntity.ok(response);
    }


}
