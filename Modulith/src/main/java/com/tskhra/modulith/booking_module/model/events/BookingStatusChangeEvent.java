package com.tskhra.modulith.booking_module.model.events;

import com.tskhra.modulith.booking_module.model.enums.BookingStatus;

import java.time.LocalDate;

public record BookingStatusChangeEvent(
    Long serviceId,
    Long businessId,
    BookingStatus newStatus,
    LocalDate date,
    int time
) {
}
