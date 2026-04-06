package com.tskhra.modulith.booking_module.model.events;

import org.springframework.modulith.events.Externalized;

import java.time.LocalDateTime;

@Externalized("bookings")
public record BookingRejectedEvent(
        String eventId,
        LocalDateTime eventTimestamp,
        String eventType,
        String entityId,
        Payload payload
) {
    public record Payload(
            String businessId,
            String bookingId
    ) {
    }
}
