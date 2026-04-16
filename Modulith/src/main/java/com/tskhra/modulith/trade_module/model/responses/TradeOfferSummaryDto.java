package com.tskhra.modulith.trade_module.model.responses;

import com.tskhra.modulith.trade_module.model.enums.TradeStatus;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

public record TradeOfferSummaryDto(
        UUID id,
        Long offererId,
        Long responderId,
        TradeStatus status,
        BigDecimal fairnessRatio,
        Instant expiresAt,
        List<OfferItemDto> offererItems,
        List<OfferItemDto> responderItems,
        LocalDateTime createdAt
) {

    public record OfferItemDto(
            UUID itemId,
            String name,
            String image
    ) {
    }
}
