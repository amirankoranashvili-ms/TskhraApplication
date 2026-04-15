package com.tskhra.modulith.trade_module.model.requests;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.util.List;
import java.util.UUID;

public record TradeOfferCreationDto(
        @NotNull Long responderId,

        @NotNull @Size(min = 1, max = 10)
        List<UUID> offererItems,

        @NotNull @Size(min = 1, max = 10)
        List<UUID> responderItems
) {
}
