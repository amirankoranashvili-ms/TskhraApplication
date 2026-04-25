package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.elastic.services.ItemSearchService;
import com.tskhra.modulith.trade_module.model.enums.ItemCondition;
import com.tskhra.modulith.trade_module.model.enums.SortByDate;
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

import java.util.List;

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
            @RequestParam(defaultValue = "false") boolean vipOnly,
            @RequestParam(defaultValue = "NEWEST") SortByDate sortByDate,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "12") int size,
            @RequestParam(required = false) Integer itemTypeId) {

        ItemSearchRequest request = new ItemSearchRequest(
                query, categoryId, cityId, condition, tradeRange, vipOnly, sortByDate, page, size, itemTypeId
        );

        return ResponseEntity.ok(itemSearchService.search(request));
    }

    @Operation(summary = "Get search suggestions based on partial input")
    @GetMapping("/suggest")
    public ResponseEntity<List<String>> suggest(
            @RequestParam String query,
            @RequestParam(defaultValue = "10") int limit) {
        return ResponseEntity.ok(itemSearchService.suggest(query, limit));
    }
}
