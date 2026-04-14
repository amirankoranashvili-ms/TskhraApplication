package com.tskhra.modulith.trade_module.model.requests;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.tskhra.modulith.trade_module.model.enums.ItemCondition;
import com.tskhra.modulith.trade_module.model.enums.TradeRange;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public record ItemUploadDto(
        @NotBlank String title,
        String description,
        @NotNull Long categoryId,
        @NotNull Long cityId,
        @NotNull ItemCondition condition,
        @NotNull TradeRange tradeRange,
        List<Long> desiredCategories

) {
}
