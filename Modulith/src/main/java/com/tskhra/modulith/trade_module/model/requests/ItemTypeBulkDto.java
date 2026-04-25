package com.tskhra.modulith.trade_module.model.requests;

public record ItemTypeBulkDto(
        String categorySlug,
        String name,
        String slug
) {}
