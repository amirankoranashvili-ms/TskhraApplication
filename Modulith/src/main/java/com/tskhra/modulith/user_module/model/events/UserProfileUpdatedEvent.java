package com.tskhra.modulith.user_module.model.events;

import org.springframework.modulith.events.Externalized;

import java.time.LocalDateTime;

@Externalized("users")
public record UserProfileUpdatedEvent(
        String eventId,
        LocalDateTime eventTimestamp,
        String eventType,
        String entityId,
        Payload payload
) {
    public record Payload(
            String userId,
            String firstName,
            String lastName,
            String gender,
            String birthDate,
            String phoneNumber
    ) {
    }
}