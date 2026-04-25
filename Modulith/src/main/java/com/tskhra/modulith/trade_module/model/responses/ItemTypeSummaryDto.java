package com.tskhra.modulith.trade_module.model.responses;

public record ItemTypeSummaryDto(
        Integer id,
        Integer categoryId,
        String categoryName,
        String name,
        String slug
) {}
