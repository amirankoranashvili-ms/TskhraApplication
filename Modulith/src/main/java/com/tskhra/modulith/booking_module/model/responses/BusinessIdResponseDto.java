package com.tskhra.modulith.booking_module.model.responses;

import java.util.UUID;

public record BusinessIdResponseDto(
        String businessId,
        String providerId
) {
}
