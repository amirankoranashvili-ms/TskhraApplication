package com.tskhra.modulith.user_module.model.events;

import org.springframework.modulith.events.Externalized;

import java.time.LocalDateTime;

@Externalized("users")
public record UserRegisteredEvent(
        String userId,
        String username,
        String email,
        LocalDateTime registeredAt
) {
}
