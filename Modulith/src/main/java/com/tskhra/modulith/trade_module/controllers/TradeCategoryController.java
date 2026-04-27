package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.responses.ItemTypeAttributeSummaryDto;
import com.tskhra.modulith.trade_module.model.responses.ItemTypeSummaryDto;
import com.tskhra.modulith.trade_module.model.responses.TradeCategorySummaryDto;
import com.tskhra.modulith.trade_module.model.responses.TradeCategoryTreeDto;
import com.tskhra.modulith.trade_module.services.ItemTypeAdminService;
import com.tskhra.modulith.trade_module.services.ItemTypeAttributeAdminService;
import com.tskhra.modulith.trade_module.services.TradeCategoryAdminService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@Tag(name = "Trade Categories", description = "Browse trade categories and item types")
@RestController
@RequestMapping("/trade-categories")
@RequiredArgsConstructor
public class TradeCategoryController {

    private final TradeCategoryAdminService categoryService;
    private final ItemTypeAdminService itemTypeService;
    private final ItemTypeAttributeAdminService itemTypeAttributeService;

    @Operation(summary = "Get full trade category tree")
    @GetMapping("/tree")
    public ResponseEntity<List<TradeCategoryTreeDto>> getCategoryTree() {
        return ResponseEntity.ok(categoryService.getCategoryTree());
    }

    @Operation(summary = "List all root trade categories")
    @GetMapping
    public ResponseEntity<List<TradeCategorySummaryDto>> listAll() {
        return ResponseEntity.ok(categoryService.findAllParents());
    }

    @Operation(summary = "List children of a category")
    @GetMapping("/{categoryId}/children")
    public ResponseEntity<List<TradeCategorySummaryDto>> listChildren(@PathVariable Integer categoryId) {
        return ResponseEntity.ok(categoryService.findChildren(categoryId));
    }

    @Operation(summary = "List item types for a category")
    @GetMapping("/{categoryId}/item-types")
    public ResponseEntity<List<ItemTypeSummaryDto>> getItemTypes(@PathVariable Integer categoryId) {
        return ResponseEntity.ok(itemTypeService.findAllByCategoryId(categoryId));
    }

    @Operation(summary = "List attributes for an item type")
    @GetMapping("/item-types/{itemTypeId}/attributes")
    public ResponseEntity<List<ItemTypeAttributeSummaryDto>> getAttributes(@PathVariable Integer itemTypeId) {
        return ResponseEntity.ok(itemTypeAttributeService.findAllByItemTypeId(itemTypeId));
    }

}
