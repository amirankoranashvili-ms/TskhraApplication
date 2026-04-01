package com.tskhra.modulith.notification_module.controllers;

import com.tskhra.modulith.notification_module.model.domain.FcmToken;
import com.tskhra.modulith.notification_module.model.dto.FcmTokenDto;
import com.tskhra.modulith.notification_module.model.dto.StatusDto;
import com.tskhra.modulith.notification_module.repositories.FcmTokenRepository;
import com.tskhra.modulith.user_module.services.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/notifications")
@RequiredArgsConstructor
public class FcmTokenController {

    private final FcmTokenRepository fcmTokenRepository;
    private final UserService userService;

    @PostMapping("/fcm-token")
    public ResponseEntity<StatusDto> registerToken(@Valid @RequestBody FcmTokenDto dto,
                                                   @AuthenticationPrincipal Jwt jwt) {

        Long userId = userService.getCurrentUser(jwt).getId();

        Optional<FcmToken> existing = fcmTokenRepository.findByToken(dto.token());
        if (existing.isPresent()) {
            FcmToken fcmToken = existing.get();
            fcmToken.setUserId(userId);
            fcmTokenRepository.save(fcmToken);
        } else {
            fcmTokenRepository.save(FcmToken.builder()
                    .userId(userId)
                    .token(dto.token())
                    .build());
        }

        return ResponseEntity.ok(new StatusDto("Registered Succesfully", LocalDateTime.now()));
    }

    @DeleteMapping("/fcm-token")
    public ResponseEntity<StatusDto> unregisterToken(@Valid @RequestBody FcmTokenDto dto) {

        fcmTokenRepository.findByToken(dto.token()).ifPresent(fcmTokenRepository::delete);
        return ResponseEntity.ok(new StatusDto("Unregistered Succesfully", LocalDateTime.now()));
    }
}
