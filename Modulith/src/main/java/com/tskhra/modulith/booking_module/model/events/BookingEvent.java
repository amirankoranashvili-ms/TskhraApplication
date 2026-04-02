package com.tskhra.modulith.booking_module.model.events;

import java.time.LocalDate;

public record BookingEvent(
        Long businessId,
        String bookedBy, // name ? name : username
        Long serviceId,
        LocalDate date,
        int time

) {
}
