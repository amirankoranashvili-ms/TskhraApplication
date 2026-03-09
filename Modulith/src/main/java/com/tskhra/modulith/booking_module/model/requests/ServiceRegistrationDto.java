package com.tskhra.modulith.booking_module.model.requests;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

import java.math.BigDecimal;

public record ServiceRegistrationDto(
        @NotBlank String name,
        String description,
        @NotNull @Positive BigDecimal price,
        @Positive int duration
) {
}
