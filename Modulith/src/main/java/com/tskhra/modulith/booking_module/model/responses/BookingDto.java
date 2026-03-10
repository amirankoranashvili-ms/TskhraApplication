package com.tskhra.modulith.booking_module.model.responses;

import com.tskhra.modulith.booking_module.model.enums.BookingStatus;

public record BookingDto(
        String id,
        String serviceName,
        String userName,
        int startTime,
        int duration,
        BookingStatus status
) {
}
