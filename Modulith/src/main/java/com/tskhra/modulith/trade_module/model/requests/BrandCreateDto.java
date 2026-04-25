package com.tskhra.modulith.trade_module.model.requests;

import jakarta.validation.constraints.NotBlank;

public record BrandCreateDto(
        @NotBlank String name,
        @NotBlank String slug
) {}
