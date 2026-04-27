package com.tskhra.modulith.trade_module.model.responses;

import com.tskhra.modulith.trade_module.model.enums.ChainStatus;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

public record ChainTradeSummaryDto(
        UUID chainId,
        ChainStatus status,
        Long initiatorId,
        List<ChainLinkSummaryDto> links,
        Instant expiresAt,
        LocalDateTime createdAt
) {

    public record ChainLinkSummaryDto(
            int position,
            Long giverId,
            UUID itemId,
            String itemName,
            Long receiverId,
            boolean accepted,
            boolean confirmed
    ) {
    }

}
