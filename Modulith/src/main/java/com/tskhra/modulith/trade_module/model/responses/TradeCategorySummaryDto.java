package com.tskhra.modulith.trade_module.model.responses;

public record TradeCategorySummaryDto(
        Integer id,
        String name,
        String slug,
        Integer parentId,
        String parentName
) {}
