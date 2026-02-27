package com.tskhra.modulith.user_module.controllers;

import com.tskhra.modulith.user_module.model.requests.LoginRequestDto;
import com.tskhra.modulith.user_module.model.requests.RefreshTokenRequest;
import com.tskhra.modulith.user_module.model.responses.TokensResponse;
import com.tskhra.modulith.user_module.services.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController { // todo /login and /refresh endpoints for mobile

    private final AuthService authService;

    @PostMapping("/login")
    public ResponseEntity<TokensResponse> login(@RequestBody LoginRequestDto dto) {
        TokensResponse tokens = authService.login(dto);
        return ResponseEntity.ok(tokens);
    }

    @PostMapping("/refresh")
    public ResponseEntity<TokensResponse> refresh(@RequestBody RefreshTokenRequest dto) {
        TokensResponse token = authService.refreshToken(dto);
        return ResponseEntity.ok(token);
    }


}
