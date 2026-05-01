package com.tskhra.modulith.booking_module.model.requests;

import com.fasterxml.jackson.annotation.JsonProperty;

public record ProviderCreateRequest(
        String name,
        String slug,
        String category,
        @JsonProperty("bot_name") String botName,
        @JsonProperty("business_id") Long businessId
) {
}
