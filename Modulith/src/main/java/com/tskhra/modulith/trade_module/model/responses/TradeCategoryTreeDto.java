package com.tskhra.modulith.trade_module.model.responses;

import java.util.List;

public record TradeCategoryTreeDto(
        Integer id,
        String name,
        String slug,
        List<TradeCategoryTreeDto> children
) {}