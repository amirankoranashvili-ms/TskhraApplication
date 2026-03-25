package com.tskhra.modulith.booking_module.model.requests;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.tskhra.modulith.booking_module.model.embeddable.WeekTimeInterval;
import com.tskhra.modulith.booking_module.model.enums.CallType;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

import java.util.List;

//@JsonIgnoreProperties(ignoreUnknown = true)
public record BusinessRegistrationDto(
        @NotBlank String businessName,
//        @NotBlank String businessNameKa,
        @NotNull CallType callType,
//        @NotBlank String city,
        @NotBlank Long cityId,
        String addressDetails,
//        String addressDetailsKa,
        @NotBlank String description,
//        @NotBlank String descriptionKa,
        @NotBlank String subCategory,
        @NotEmpty List<@Valid WeekTimeInterval> workTimes,
        List<@Valid WeekTimeInterval> restTimes,
        @Valid Info info
) {
}
