package com.tskhra.modulith.booking_module.model.requests;

public record BusinessWithCountDto(BusinessDetailsDto business, int awaitingBookingCount) {
}