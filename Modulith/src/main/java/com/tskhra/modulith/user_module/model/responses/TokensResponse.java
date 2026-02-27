package com.tskhra.modulith.user_module.model.responses;

import com.fasterxml.jackson.annotation.JsonProperty;

public record TokensResponse(
        @JsonProperty("access_token") String accessToken,
        @JsonProperty("refresh_token") String refreshToken,
        @JsonProperty("expires_in") int expiresIn,
        @JsonProperty("refresh_expires_in") int refreshExpiresIn,
        @JsonProperty("token_type") String tokenType
) {
}
