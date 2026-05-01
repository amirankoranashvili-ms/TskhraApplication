package com.tskhra.modulith.booking_module.model.responses;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public record ProviderCreateResponse(
        @JsonProperty("provider_id") String providerId,
        @JsonProperty("api_key") String apiKey
) {
}
