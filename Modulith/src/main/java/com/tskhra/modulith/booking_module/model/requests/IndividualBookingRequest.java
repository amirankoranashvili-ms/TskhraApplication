package com.tskhra.modulith.booking_module.model.requests;

import java.time.LocalDate;

public record IndividualBookingRequest(
        String serviceId,
        LocalDate date,
        int startTime
) {
}
