package com.tskhra.modulith.user_module.model.requests;

public record BiometricsDto(
        String deviceId,
        String publicKey
) {
}
