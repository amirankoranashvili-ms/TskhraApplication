package com.tskhra.modulith.common.services;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class NotificationService {

    private final SimpMessagingTemplate messagingTemplate;

    @Async
    public void sendToUser(String userId, Object payload) {
        try {
            messagingTemplate.convertAndSendToUser(userId, "/queue/notifications", payload);
            log.debug("Notification sent to user {}", userId);
        } catch (Exception e) {
            log.error("Failed to send notification to user {}: {}", userId, e.getMessage(), e);
        }
    }

    @Async
    public void sendToTopic(String topicName, Object payload) {
        try {
            messagingTemplate.convertAndSend("/topic/" + topicName, payload);
            log.debug("Notification sent to topic {}", topicName);
        } catch (Exception e) {
            log.error("Failed to send notification to topic {}: {}", topicName, e.getMessage(), e);
        }
    }
}
