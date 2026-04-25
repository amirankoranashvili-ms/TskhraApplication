package com.tskhra.modulith.trade_module.model.requests;

public record TradeCategoryBulkDto(
        String name,
        String slug,
        String parentSlug
) {}
