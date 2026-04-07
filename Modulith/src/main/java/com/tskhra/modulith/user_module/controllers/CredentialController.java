package com.tskhra.modulith.user_module.controllers;

import com.tskhra.modulith.user_module.model.enums.CredentialType;
import com.tskhra.modulith.user_module.model.requests.ChallengeRequest;
import com.tskhra.modulith.user_module.model.requests.CredentialUpdateRequest;
import com.tskhra.modulith.user_module.model.requests.CredentialsRegisterRequest;
import com.tskhra.modulith.user_module.model.requests.VerifyRequest;
import com.tskhra.modulith.user_module.model.responses.ChallengeResponse;
import com.tskhra.modulith.user_module.model.responses.MessageResponse;
import com.tskhra.modulith.user_module.model.responses.TokensResponse;
import com.tskhra.modulith.user_module.services.CredentialService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;

@RestController
@RequestMapping("/auth/credentials")
@RequiredArgsConstructor
public class CredentialController {

    private final CredentialService credentialService;

    @PostMapping
    public ResponseEntity<MessageResponse> registerDevice(@AuthenticationPrincipal Jwt jwt,
                                                          @RequestBody CredentialsRegisterRequest request) {
        credentialService.registerDevice(request, jwt);
        MessageResponse body = new MessageResponse(
                HttpStatus.CREATED.value(),
                "Device registered successfully",
                Instant.now().toString()
        );
        return ResponseEntity.ok(body);
    }

    @PostMapping("/challenge")
    public ResponseEntity<ChallengeResponse> generateChallenge(@RequestBody ChallengeRequest challengeRequest) {
        String challenge = credentialService.generateChallenge(challengeRequest);
        ChallengeResponse body = new ChallengeResponse(
                HttpStatus.OK.value(),
                "Challenge generated successfully",
                Instant.now().toString(),
                challenge
        );
        return ResponseEntity.ok(body);
    }

    @PostMapping("/verify")
    public ResponseEntity<TokensResponse> verifyAndLogin(@RequestBody VerifyRequest request,
                                                         @RequestParam("type") CredentialType type) {
        TokensResponse tokens = credentialService.verifyAndLogin(request, type);
        return ResponseEntity.ok(tokens);
    }

    @PutMapping("/rotate")
    public ResponseEntity<Void> updatePublicKey(@RequestBody CredentialUpdateRequest credentialUpdateRequest,
                                                @RequestParam("type") CredentialType type) {
        credentialService.updatePublicKey(credentialUpdateRequest, type);
        return ResponseEntity.noContent().build();
    }

}
