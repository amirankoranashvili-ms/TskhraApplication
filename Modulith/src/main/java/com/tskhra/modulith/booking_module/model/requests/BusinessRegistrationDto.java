package com.tskhra.modulith.booking_module.model.requests;

import com.tskhra.modulith.booking_module.model.embeddable.WeekTimeInterval;
import com.tskhra.modulith.booking_module.model.enums.CallType;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import java.util.List;

public record BusinessRegistrationDto(
        @NotBlank
        String businessName,
        @NotNull
        CallType callType,
        @NotBlank
        String city,
        String addressDetails,
        @NotBlank
        String description,
        String mainPhotoId,
        List<String> galleryPhotoIds,
        @NotBlank
        String subCategory,
        @NotEmpty
        List<@Valid WeekTimeInterval> workTimes,
        List<@Valid WeekTimeInterval> restTimes,
        @Valid
        Info info
) {
}
