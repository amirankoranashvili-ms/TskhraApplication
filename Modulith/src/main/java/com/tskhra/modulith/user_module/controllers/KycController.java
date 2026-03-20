package com.tskhra.modulith.user_module.controllers;

import com.tskhra.modulith.user_module.model.responses.KycTokenResponse;
import com.tskhra.modulith.user_module.services.KycService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/kyc")
@RequiredArgsConstructor
public class KycController {

    private final KycService kycService;

    @GetMapping("/token")
    public ResponseEntity<KycTokenResponse> verify(@AuthenticationPrincipal Jwt jwt) {

        KycTokenResponse response = kycService.getAccessToken(jwt);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/webhook")
    public ResponseEntity<Void> verifyWebhook(@RequestBody String body) {
        kycService.handleWebhook(body);
        return ResponseEntity.ok().build();
    }
}
