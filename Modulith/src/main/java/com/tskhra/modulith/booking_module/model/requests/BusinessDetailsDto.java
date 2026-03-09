package com.tskhra.modulith.booking_module.model.requests;

import com.tskhra.modulith.booking_module.model.embeddable.WeekTimeInterval;
import com.tskhra.modulith.booking_module.model.enums.CallType;

import java.util.List;

public record BusinessDetailsDto(
        String businessId,
        String businessName,
        String category,
        String subCategory,
        String mainImage,
        List<String> galleryImages,
        String city,
        String addressDetail,
        CallType callType,
        List<WeekTimeInterval> workTimes,
        List<WeekTimeInterval> restTimes,
        Info info,
        String description
        // info
        // description

) {
}
