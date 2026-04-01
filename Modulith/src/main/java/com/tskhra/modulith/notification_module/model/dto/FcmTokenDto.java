package com.tskhra.modulith.notification_module.model.dto;

import jakarta.validation.constraints.NotBlank;

public record FcmTokenDto(
        @NotBlank String token
) {
}