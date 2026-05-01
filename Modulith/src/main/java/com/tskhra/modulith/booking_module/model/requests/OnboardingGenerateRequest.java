package com.tskhra.modulith.booking_module.model.requests;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Map;

public record OnboardingGenerateRequest(
        @JsonProperty("business_id") Long businessId,
        String category,
        Map<String, String> answers
) {
}