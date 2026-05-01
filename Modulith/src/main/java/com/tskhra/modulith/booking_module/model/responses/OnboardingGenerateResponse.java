package com.tskhra.modulith.booking_module.model.responses;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public record OnboardingGenerateResponse(
        @JsonProperty("provider_id") String providerId,
        @JsonProperty("chat_api_key") String chatApiKey
) {
}
