package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.services.NotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/notifications")
@RequiredArgsConstructor
public class NotificationController {

    private final NotificationService notificationService;

    @GetMapping("/count")
    public ResponseEntity<Integer> getNotificationCount(@AuthenticationPrincipal Jwt jwt) {

        int count = notificationService.getNotificationCountByUser(jwt);
        return ResponseEntity.ok(count);
    }

}
