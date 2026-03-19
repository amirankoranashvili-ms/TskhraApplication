package com.tskhra.modulith.user_module.model.responses;

public record KycTokenResponse(
        String token,
        String userId
) {
}
