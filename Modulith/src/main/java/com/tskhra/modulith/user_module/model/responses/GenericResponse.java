package com.tskhra.modulith.user_module.model.responses;

import org.springframework.http.HttpStatus;

import java.time.LocalDateTime;

public record GenericResponse(
        HttpStatus status,
        String message,
        LocalDateTime timestamp,
        Object data
) {
}
