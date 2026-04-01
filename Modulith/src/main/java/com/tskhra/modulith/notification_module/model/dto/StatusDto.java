package com.tskhra.modulith.notification_module.model.dto;

import java.time.LocalDateTime;

public record StatusDto(
        String message,
        LocalDateTime timestamp
) {
}
