package com.tskhra.modulith.trade_module.model.requests;

import jakarta.validation.constraints.NotNull;

import java.util.Map;

public record ItemTypeAttributeCreateDto(
        @NotNull Integer itemTypeId,
        @NotNull Integer attributeId,
        boolean required,
        boolean filterable,
        Map<String, Object> constraints
) {}
