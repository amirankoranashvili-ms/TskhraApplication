package com.tskhra.modulith.user_module.model.events;

import org.springframework.modulith.events.Externalized;

import java.time.LocalDateTime;

@Externalized("users")
public record UserProfilePictureUpdatedEvent(
        String eventId,
        LocalDateTime eventTimestamp,
        String eventType,
        String entityId,
        Payload payload
) {
    public record Payload(
            String userId,
            String imageUri
    ) {
    }
}