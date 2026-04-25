package com.tskhra.modulith.trade_module.model.requests;

import java.util.Map;

public record ItemTypeAttributeBulkDto(
        String itemTypeSlug,
        String attributeKey,
        boolean required,
        boolean filterable,
        Map<String, Object> constraints
) {}
