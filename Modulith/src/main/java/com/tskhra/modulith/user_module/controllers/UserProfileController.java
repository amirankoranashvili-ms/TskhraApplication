package com.tskhra.modulith.user_module.controllers;

import com.tskhra.modulith.booking_module.validation.ImageFile;
import com.tskhra.modulith.user_module.model.requests.UserProfileUpdateDto;
import io.swagger.v3.oas.annotations.Operation;
import com.tskhra.modulith.user_module.model.responses.UserProfileSelfDto;
import com.tskhra.modulith.user_module.services.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/user-profile")
@RequiredArgsConstructor
@Validated
public class UserProfileController {

    private final UserService userService;

    @Operation(summary = "Get current user's profile")
    @GetMapping("/me")
    public ResponseEntity<UserProfileSelfDto> getCurrentUserProfile(@AuthenticationPrincipal Jwt jwt) {

        UserProfileSelfDto dto = userService.getCurrentUserProfile(jwt);
        return ResponseEntity.ok(dto);
    }

    @Operation(summary = "Update current user's profile")
    @PostMapping("/me")
    public ResponseEntity<Void> updateUserProfile(@AuthenticationPrincipal Jwt jwt,
                                                  @Valid @RequestBody UserProfileUpdateDto dto) {

        userService.updateProfile(dto, jwt);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

    @Operation(summary = "Upload user avatar")
    @PostMapping(value = "/me/avatar", consumes = MediaType.MULTIPART_FORM_DATA_VALUE) // todo PUT more correct?
    public ResponseEntity<Void> updateAvatar(@AuthenticationPrincipal Jwt jwt,
                                             @ImageFile @RequestParam("file") MultipartFile file) {

        userService.uploadAvatar(file, jwt);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT); // todo OK?
    }

    @Operation(summary = "Delete user avatar")
    @DeleteMapping("/me/avatar")
    public ResponseEntity<Void> deleteAvatar(@AuthenticationPrincipal Jwt jwt) {

        userService.deleteAvatar(jwt);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
