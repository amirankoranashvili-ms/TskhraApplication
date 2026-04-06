package com.tskhra.modulith.booking_module.model.events;

import org.springframework.modulith.events.Externalized;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Externalized("businesses")
public record ServiceCreatedEvent(
        String eventId,
        LocalDateTime eventTimestamp,
        String eventType,
        String entityId,
        Payload payload
) {
    public record Payload(
            String businessId,
            String serviceId,
            String name,
            String nameKa,
            String description,
            String descriptionKa,
            BigDecimal price,
            int duration
    ) {
    }
}
