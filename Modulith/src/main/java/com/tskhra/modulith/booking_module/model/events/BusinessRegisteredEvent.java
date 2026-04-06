package com.tskhra.modulith.booking_module.model.events;

import org.springframework.modulith.events.Externalized;

import java.time.LocalDateTime;
import java.util.List;

@Externalized("businesses")
public record BusinessRegisteredEvent(
        String eventId,
        LocalDateTime eventTimestamp,
        String eventType,
        String entityId,
        Payload payload
) {
    public record Payload(
            String businessId,
            String businessName,
            String businessNameKa,
            String callType,
            Long cityId,
            String addressDetails,
            String addressDetailsKa,
            String description,
            String descriptionKa,
            Long subcategoryId,
            List<TimeInterval> workTimes,
            List<TimeInterval> restTimes,
            InfoPayload info
    ) {
    }

    public record TimeInterval(
            String weekDay,
            int startTime,
            int endTime
    ) {
    }

    public record InfoPayload(
            String phoneNumber,
            String instagramUrl,
            String facebookUrl
    ) {
    }
}
