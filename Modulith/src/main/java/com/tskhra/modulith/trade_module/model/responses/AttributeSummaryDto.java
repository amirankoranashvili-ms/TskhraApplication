package com.tskhra.modulith.trade_module.model.responses;

import com.tskhra.modulith.trade_module.model.enums.AttributeDataType;

public record AttributeSummaryDto(
        Integer id,
        String name,
        String key,
        AttributeDataType dataType,
        String unit
) {}
