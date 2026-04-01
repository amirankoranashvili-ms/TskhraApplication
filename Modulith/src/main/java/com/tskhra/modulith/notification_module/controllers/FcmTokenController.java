package com.tskhra.modulith.notification_module.controllers;

import com.tskhra.modulith.notification_module.model.domain.FcmToken;
import com.tskhra.modulith.notification_module.repositories.FcmTokenRepository;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/notifications")
@RequiredArgsConstructor
public class FcmTokenController {

    private final FcmTokenRepository fcmTokenRepository;
    private final UserService userService;

    @PostMapping("/fcm-token")
    public Map<String, String> registerToken(@RequestBody Map<String, String> body,
                                             JwtAuthenticationToken auth) {
        String token = body.get("token");
        Jwt jwt = auth.getToken();
        Long userId = userService.getCurrentUser(jwt).getId();

        // If this token already exists (same device re-registering), update the userId.
        // If it's new, create it. This handles the case where a user logs out
        // and another user logs in on the same device.
        Optional<FcmToken> existing = fcmTokenRepository.findByToken(token);
        if (existing.isPresent()) {
            FcmToken fcmToken = existing.get();
            fcmToken.setUserId(userId);
            fcmTokenRepository.save(fcmToken);
        } else {
            fcmTokenRepository.save(FcmToken.builder()
                    .userId(userId)
                    .token(token)
                    .build());
        }

        return Map.of("status", "registered");
    }

    @DeleteMapping("/fcm-token")
    public Map<String, String> unregisterToken(@RequestBody Map<String, String> body) {
        String token = body.get("token");
        fcmTokenRepository.findByToken(token).ifPresent(fcmTokenRepository::delete);
        return Map.of("status", "unregistered");
    }
}
