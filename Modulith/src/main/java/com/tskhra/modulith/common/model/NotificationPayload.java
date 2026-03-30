package com.tskhra.modulith.common.model;

import org.springframework.modulith.NamedInterface;

import java.time.LocalDateTime;

@NamedInterface
public record NotificationPayload(
        String type,
        String title,
        String message,
        Object data,
        LocalDateTime timestamp
) {
}
