package com.tskhra.modulith.booking_module.model.enums;

import org.springframework.modulith.NamedInterface;

@NamedInterface
public enum BookingStatus {
    AWAITING, SCHEDULED, REJECTED, CANCELLED_BY_BUSINESS, CANCELLED_BY_USER, COMPLETED
}
