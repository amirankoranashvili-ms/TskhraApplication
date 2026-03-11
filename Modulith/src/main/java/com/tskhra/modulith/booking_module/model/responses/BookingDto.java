package com.tskhra.modulith.booking_module.model.responses;

import com.tskhra.modulith.booking_module.model.enums.BookingStatus;

import java.time.LocalDate;

public record BookingDto(
        String id,
        String serviceName,
        String userName,
        int startTime,
        int duration,
        BookingStatus status,
        LocalDate date) {
}
