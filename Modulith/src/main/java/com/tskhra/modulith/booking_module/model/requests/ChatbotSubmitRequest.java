package com.tskhra.modulith.booking_module.model.requests;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import java.util.Map;

public record ChatbotSubmitRequest(
        @NotNull Long businessId,
        @NotEmpty Map<String, String> answers
) {
}
