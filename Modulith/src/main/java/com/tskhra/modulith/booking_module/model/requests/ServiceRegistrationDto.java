package com.tskhra.modulith.booking_module.model.requests;

import jakarta.validation.constraints.*;

import java.math.BigDecimal;

public record ServiceRegistrationDto(
        @NotBlank
        @Size(max = 50, message = "Name must be at most 50 characters")
        String name,

        @Size(max = 100, message = "Description must be at most 100 characters")
        String description,

        @NotNull
        @Positive
        @DecimalMax(value = "1000000", message = "Price must not exceed 1,000,000")
        @Digits(integer = 7, fraction = 2, message = "Price must have a maximum of 2 decimal places")
        BigDecimal price,

        @Positive
        @Max(value = 1439, message = "Duration must be less than 1440")
        int duration
) {
}
