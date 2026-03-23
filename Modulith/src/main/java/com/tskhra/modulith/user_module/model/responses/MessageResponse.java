package com.tskhra.modulith.user_module.model.responses;

public record MessageResponse(
        int statusCode,
        String message,
        String timestamp
) {
}
