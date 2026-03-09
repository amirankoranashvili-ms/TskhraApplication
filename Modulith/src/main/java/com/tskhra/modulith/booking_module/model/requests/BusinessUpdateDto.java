package com.tskhra.modulith.booking_module.model.requests;

import com.tskhra.modulith.booking_module.model.enums.CallType;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record BusinessUpdateDto(
        @NotBlank String businessName,
        @NotNull CallType callType,
        @NotBlank String description,
        @Valid Info info
) {
}
