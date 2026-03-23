package com.tskhra.modulith.common.exception;


public record ErrorResponse(
        int statusCode,
        String message,
        String timestamp
) {
}
