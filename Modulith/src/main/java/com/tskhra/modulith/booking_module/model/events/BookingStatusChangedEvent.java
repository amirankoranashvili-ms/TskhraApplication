package com.tskhra.modulith.booking_module.model.events;

import com.tskhra.modulith.booking_module.model.enums.BookingStatus;
import org.springframework.modulith.NamedInterface;

@NamedInterface
public record BookingStatusChangedEvent(
        Long bookingId,
        Long recipientUserId,
        BookingStatus newStatus,
        String serviceName,
        String businessName
) {
}
