package com.tskhra.modulith.trade_module.model.requests;

import com.tskhra.modulith.trade_module.model.enums.ItemCondition;
import com.tskhra.modulith.trade_module.model.enums.TradeRange;

import java.math.BigDecimal;

public record ItemSearchRequest(
        String query,
        Long categoryId,
        Long cityId,
        ItemCondition condition,
        TradeRange tradeRange,
        BigDecimal minPrice,
        BigDecimal maxPrice,
        int page,
        int size
) {
}
