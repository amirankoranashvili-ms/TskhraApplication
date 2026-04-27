package com.tskhra.modulith.trade_module.model.responses;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

public record ChainCandidateDto(
        List<ChainLinkDto> links,
        int length
) {

    public record ChainLinkDto(
            int position,
            UUID itemId,
            String itemName,
            Long ownerId,
            String categoryName,
            BigDecimal estimatedValue
    ) {
    }

}
