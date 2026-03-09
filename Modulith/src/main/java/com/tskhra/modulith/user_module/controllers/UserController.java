package com.tskhra.modulith.user_module.controllers;

import com.tskhra.modulith.user_module.model.requests.KeycloakSpiUserRegistrationDto;
import com.tskhra.modulith.user_module.model.requests.UserRegistrationRequestDto;
import com.tskhra.modulith.user_module.model.responses.UserSelfDto;
import com.tskhra.modulith.user_module.services.UserService;
import io.swagger.v3.oas.annotations.Hidden;
import io.swagger.v3.oas.annotations.Operation;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @Operation(summary = "Register a new user")
    @PostMapping("/register")
    public ResponseEntity<Void> registerUser(@Valid @RequestBody UserRegistrationRequestDto dto) {

        userService.registerUser(dto);
        return new ResponseEntity<>(HttpStatus.CREATED);
    }

    // todo figure how to make it safe
    @Hidden
    @PostMapping("/kc-register")
    public ResponseEntity<Void> registerKcUser(@RequestBody KeycloakSpiUserRegistrationDto dto) {

        userService.registerKcUser(dto);
        return new ResponseEntity<>(HttpStatus.CREATED);
    }

    @Operation(summary = "Get current user info")
    @GetMapping("/me")
    public ResponseEntity<UserSelfDto> getCurrentUser(@AuthenticationPrincipal Jwt jwt) {

        UserSelfDto self = userService.getCurrentUserInfo(jwt);
        return ResponseEntity.status(HttpStatus.OK).body(self);
    }

    @Operation(summary = "Health check")
    @GetMapping("/sanity-check")
    public ResponseEntity<String> sanityCheck() {
        return ResponseEntity.ok("Sanity check passed!");
    }

    @Operation(summary = "Verify current user")
    @PostMapping("/me/verify")
    public ResponseEntity<Void> selfVerify(@AuthenticationPrincipal Jwt jwt) {
        userService.selfVerify(jwt);
        return new ResponseEntity<>(HttpStatus.OK);
    }

    @Operation(summary = "Unverify current user")
    @PostMapping("/me/unverify")
    public ResponseEntity<Void> selfUnverify(@AuthenticationPrincipal Jwt jwt) {
        userService.selfUnverify(jwt);
        return new ResponseEntity<>(HttpStatus.OK);
    }

}
