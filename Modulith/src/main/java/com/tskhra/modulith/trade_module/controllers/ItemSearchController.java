package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.elastic.services.ItemSearchService;
import com.tskhra.modulith.trade_module.model.enums.ItemCondition;
import com.tskhra.modulith.trade_module.model.enums.TradeRange;
import com.tskhra.modulith.trade_module.model.requests.ItemSearchRequest;
import com.tskhra.modulith.trade_module.model.responses.ItemSummaryDto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;

@Tag(name = "Item Search", description = "Search and filter tradeable items")
@RestController
@RequestMapping("/items/search")
@RequiredArgsConstructor
public class ItemSearchController {

    private final ItemSearchService itemSearchService;

    @Operation(summary = "Search items with optional filters")
    @GetMapping
    public ResponseEntity<Page<ItemSummaryDto>> searchItems(
            @RequestParam(required = false) String query,
            @RequestParam(required = false) Long categoryId,
            @RequestParam(required = false) Long cityId,
            @RequestParam(required = false) ItemCondition condition,
            @RequestParam(required = false) TradeRange tradeRange,
            @RequestParam(required = false) BigDecimal minPrice,
            @RequestParam(required = false) BigDecimal maxPrice,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "12") int size) {

        ItemSearchRequest request = new ItemSearchRequest(
                query, categoryId, cityId, condition, tradeRange, minPrice, maxPrice, page, size
        );

        return ResponseEntity.ok(itemSearchService.search(request));
    }
}
