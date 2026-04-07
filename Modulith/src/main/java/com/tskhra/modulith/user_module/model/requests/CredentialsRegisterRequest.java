package com.tskhra.modulith.user_module.model.requests;

import com.tskhra.modulith.user_module.model.enums.CredentialType;
import jakarta.validation.constraints.NotNull;
import org.hibernate.validator.constraints.UUID;

import java.util.Map;

public record CredentialsRegisterRequest(
        @UUID
        @NotNull
        String deviceId,
        Map<CredentialType, String> credentials
) {
}
