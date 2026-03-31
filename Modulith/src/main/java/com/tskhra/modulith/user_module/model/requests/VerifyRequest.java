package com.tskhra.modulith.user_module.model.requests;

public record VerifyRequest(
        String deviceId,
        String signature
) {
}
