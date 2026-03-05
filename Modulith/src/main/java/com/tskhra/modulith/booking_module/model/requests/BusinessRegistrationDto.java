package com.tskhra.modulith.booking_module.model.requests;

import com.tskhra.modulith.booking_module.model.embeddable.WeekTimeInterval;
import com.tskhra.modulith.booking_module.model.enums.CallType;

import java.util.List;

public record BusinessRegistrationDto(
        String businessName,
        CallType callType, // enum
        String city, // search by name
        String addressDetails, // just address details
        String description,
        String mainImageId,
        List<String> galleryImageIds,
        String subCategory,
        List<WeekTimeInterval> workTimes,
        List<WeekTimeInterval> restTimes,
        Info info
) {
}
