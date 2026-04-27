package com.tskhra.modulith.trade_module.model.requests;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.util.List;
import java.util.UUID;

public record ChainProposalDto(
        @NotNull @Size(min = 2, max = 8)
        List<UUID> itemIds
) {
}
