package com.tskhra.modulith.trade_module.model.responses;

import com.tskhra.modulith.trade_module.model.enums.ItemCondition;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.enums.TradeRange;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

public record ItemSummaryDto(
        UUID id,
        String name,
        String description,
        String category,
        String city,
        ItemCondition condition,
        TradeRange tradeRange,
        BigDecimal estimatedValue,
        LocalDateTime createdAt,
        List<String> images,
        ItemStatus status
) {
}
