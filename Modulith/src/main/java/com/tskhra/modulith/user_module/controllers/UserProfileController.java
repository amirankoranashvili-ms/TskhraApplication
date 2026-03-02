package com.tskhra.modulith.user_module.controllers;

import com.tskhra.modulith.user_module.model.requests.UserProfileUpdateDto;
import com.tskhra.modulith.user_module.model.responses.UserProfileSelfDto;
import com.tskhra.modulith.user_module.services.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/user-profile")
@RequiredArgsConstructor
public class UserProfileController {

    private final UserService userService;

    @GetMapping("/me")
    public ResponseEntity<UserProfileSelfDto> getCurrentUserProfile(@AuthenticationPrincipal Jwt jwt) {

        UserProfileSelfDto dto = userService.getCurrentUserProfile(jwt);
        return ResponseEntity.ok(dto);
    }

    @PostMapping("/me")
    public ResponseEntity<Void> updateUserProfile(@AuthenticationPrincipal Jwt jwt,
                                                  @Valid @RequestBody UserProfileUpdateDto dto) {

        userService.updateProfile(dto, jwt);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

// todo   @PostMapping("/me/avatar")


}
