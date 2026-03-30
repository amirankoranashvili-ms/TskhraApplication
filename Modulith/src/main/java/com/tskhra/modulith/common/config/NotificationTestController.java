package com.tskhra.modulith.common.config;

import com.tskhra.modulith.common.model.NotificationPayload;
import com.tskhra.modulith.common.services.NotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;

@RestController
@RequestMapping("/test")
@RequiredArgsConstructor
public class NotificationTestController {

    private final NotificationService notificationService;

    @PostMapping("/notify/{userId}")
    public void sendToUser(@PathVariable String userId) {
        notificationService.sendToUser(userId, new NotificationPayload(
                "TEST",
                "Test Notification",
                "This is a test notification for user " + userId,
                null,
                LocalDateTime.now()
        ));
    }

    @PostMapping("/broadcast/{topic}")
    public void sendToTopic(@PathVariable String topic) {
        notificationService.sendToTopic(topic, new NotificationPayload(
                "BROADCAST_TEST",
                "Test Broadcast",
                "This is a test broadcast to topic: " + topic,
                null,
                LocalDateTime.now()
        ));
    }
}
