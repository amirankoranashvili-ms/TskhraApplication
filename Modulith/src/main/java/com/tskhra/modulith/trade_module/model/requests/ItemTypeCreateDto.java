package com.tskhra.modulith.trade_module.model.requests;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record ItemTypeCreateDto(
        @NotNull Integer categoryId,
        @NotBlank String name,
        @NotBlank String slug
) {}
