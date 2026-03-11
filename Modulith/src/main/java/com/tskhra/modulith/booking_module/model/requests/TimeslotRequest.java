package com.tskhra.modulith.booking_module.model.requests;

import java.time.LocalDate;

public record TimeslotRequest(
        LocalDate date,
        String serviceId
) {
}
