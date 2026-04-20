package com.tskhra.modulith.trade_module.model.requests;

import com.tskhra.modulith.trade_module.model.enums.ItemCondition;
import com.tskhra.modulith.trade_module.model.enums.SortByDate;
import com.tskhra.modulith.trade_module.model.enums.TradeRange;

public record ItemSearchRequest(
        String query,
        Long categoryId,
        Long cityId,
        ItemCondition condition,
        TradeRange tradeRange,
        SortByDate sortByDate,
        int page,
        int size
) {
}
