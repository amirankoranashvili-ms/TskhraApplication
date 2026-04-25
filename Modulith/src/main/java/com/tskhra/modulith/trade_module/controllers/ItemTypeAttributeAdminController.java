package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.requests.ItemTypeAttributeBulkDto;
import com.tskhra.modulith.trade_module.model.requests.ItemTypeAttributeCreateDto;
import com.tskhra.modulith.trade_module.model.responses.BulkImportResult;
import com.tskhra.modulith.trade_module.model.responses.ItemTypeAttributeSummaryDto;
import com.tskhra.modulith.trade_module.services.ItemTypeAttributeAdminService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "Item Type Attribute Admin", description = "Manage item type attribute mappings")
@RestController
@RequestMapping("/admin/item-type-attributes")
@RequiredArgsConstructor
public class ItemTypeAttributeAdminController {

    private final ItemTypeAttributeAdminService service;

    @Operation(summary = "Link an attribute to an item type")
    @PostMapping
    public ResponseEntity<ItemTypeAttributeSummaryDto> create(@Valid @RequestBody ItemTypeAttributeCreateDto dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(dto));
    }

    @Operation(summary = "List attributes for an item type")
    @GetMapping("/by-item-type/{itemTypeId}")
    public ResponseEntity<List<ItemTypeAttributeSummaryDto>> findByItemType(@PathVariable Integer itemTypeId) {
        return ResponseEntity.ok(service.findAllByItemTypeId(itemTypeId));
    }

    @Operation(summary = "Bulk import item type attribute links")
    @PostMapping("/bulk")
    public ResponseEntity<BulkImportResult> bulkCreate(@RequestBody List<ItemTypeAttributeBulkDto> dtos) {
        return ResponseEntity.ok(service.bulkCreate(dtos));
    }

    @Operation(summary = "Export all item type attribute links")
    @GetMapping("/export")
    public ResponseEntity<List<ItemTypeAttributeBulkDto>> exportAll() {
        return ResponseEntity.ok(service.exportAll());
    }

    @Operation(summary = "Remove an item type attribute mapping")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Integer id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

}
