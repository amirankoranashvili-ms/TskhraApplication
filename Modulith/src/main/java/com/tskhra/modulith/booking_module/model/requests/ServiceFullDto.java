package com.tskhra.modulith.booking_module.model.requests;

import java.math.BigDecimal;

public record ServiceFullDto(
        String id,
        String name,
        String description,
        BigDecimal price,
        int duration
) {
}
