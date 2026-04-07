package com.tskhra.modulith.user_module.model.requests;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.hibernate.validator.constraints.UUID;

public record CredentialUpdateRequest(
        @UUID
        @NotNull
        String deviceId,
        @NotBlank
        String publicKey
) {
}
