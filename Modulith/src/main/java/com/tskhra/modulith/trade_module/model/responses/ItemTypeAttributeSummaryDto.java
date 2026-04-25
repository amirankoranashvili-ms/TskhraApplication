package com.tskhra.modulith.trade_module.model.responses;

import com.tskhra.modulith.trade_module.model.enums.AttributeDataType;

import java.util.Map;

public record ItemTypeAttributeSummaryDto(
        Integer id,
        Integer attributeId,
        String attributeName,
        String attributeKey,
        AttributeDataType dataType,
        String unit,
        boolean required,
        boolean filterable,
        Map<String, Object> constraints
) {}
