package com.tskhra.modulith.user_module.model.responses;

public record TokensResponse(
        String accessToken,
        String refreshToken,
        int expiresIn,
        int refreshExpiresIn,
        String tokenType
) {
}
