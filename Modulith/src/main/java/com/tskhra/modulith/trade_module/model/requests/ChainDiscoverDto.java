package com.tskhra.modulith.trade_module.model.requests;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

import java.util.UUID;

public record ChainDiscoverDto(
        @NotNull UUID itemId,
        @Min(2) @Max(8) int maxLength
) {
    public ChainDiscoverDto {
        if (maxLength == 0) maxLength = 6;
    }
}
