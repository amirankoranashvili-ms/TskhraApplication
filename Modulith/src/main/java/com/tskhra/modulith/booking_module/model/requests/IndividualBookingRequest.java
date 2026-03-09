package com.tskhra.modulith.booking_module.model.requests;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

import java.time.LocalDate;

public record IndividualBookingRequest(
        @NotBlank String serviceId,
        @NotNull LocalDate date,
        @PositiveOrZero @Max(1439) int startTime
) {
}
