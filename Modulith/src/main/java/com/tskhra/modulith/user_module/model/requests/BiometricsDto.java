package com.tskhra.modulith.user_module.model.requests;

import jakarta.validation.constraints.NotNull;
import org.hibernate.validator.constraints.UUID;

public record BiometricsDto(
        @UUID
        @NotNull
        String deviceId,
        String publicKey
) {
}
