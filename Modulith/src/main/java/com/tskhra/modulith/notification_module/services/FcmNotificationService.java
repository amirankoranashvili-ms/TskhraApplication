package com.tskhra.modulith.notification_module.services;

import com.google.firebase.messaging.*;
import com.tskhra.modulith.notification_module.model.domain.FcmToken;
import com.tskhra.modulith.notification_module.repositories.FcmTokenRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class FcmNotificationService {

    private final FirebaseMessaging firebaseMessaging;
    private final FcmTokenRepository fcmTokenRepository;

    public void sendToUser(Long userId, String title, String body, Map<String, String> data) {
        List<FcmToken> tokens = fcmTokenRepository.findAllByUserId(userId);

        if (tokens.isEmpty()) {
            log.debug("No FCM tokens found for user {}, skipping notification", userId);
            return;
        }

        for (FcmToken fcmToken : tokens) {
            sendToToken(fcmToken, title, body, data);
        }
    }

    private void sendToToken(FcmToken fcmToken, String title, String body, Map<String, String> data) {
        Message message = Message.builder()
                .setToken(fcmToken.getToken())
                .setNotification(Notification.builder()
                        .setTitle(title)
                        .setBody(body)
                        .build())
                .putAllData(data)
                .build();

        try {
            String messageId = firebaseMessaging.send(message);
            log.info("FCM sent to user {} (messageId: {})", fcmToken.getUserId(), messageId);
        } catch (FirebaseMessagingException e) {
            handleSendError(fcmToken, e);
        }
    }

    @Transactional
    protected void handleSendError(FcmToken fcmToken, FirebaseMessagingException e) {
        // UNREGISTERED or INVALID_ARGUMENT means the token is no longer valid.
        // This happens when the user uninstalls the app, or Firebase rotates the token.
        if (e.getMessagingErrorCode() == MessagingErrorCode.UNREGISTERED
                || e.getMessagingErrorCode() == MessagingErrorCode.INVALID_ARGUMENT) {
            log.warn("Removing invalid FCM token for user {}: {}", fcmToken.getUserId(), e.getMessage());
            fcmTokenRepository.deleteByToken(fcmToken.getToken());
        } else {
            log.error("FCM send failed for user {}: {}", fcmToken.getUserId(), e.getMessage());
        }
    }
}
