package com.tskhra.modulith.trade_module.model.requests;

import com.tskhra.modulith.trade_module.model.enums.AttributeDataType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record AttributeCreateDto(
        @NotBlank String name,
        @NotBlank String key,
        @NotNull AttributeDataType dataType,
        String unit
) {}
