package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.requests.ItemTypeBulkDto;
import com.tskhra.modulith.trade_module.model.requests.ItemTypeCreateDto;
import com.tskhra.modulith.trade_module.model.responses.BulkImportResult;
import com.tskhra.modulith.trade_module.model.responses.ItemTypeSummaryDto;
import com.tskhra.modulith.trade_module.services.ItemTypeAdminService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "Item Type Admin", description = "Manage item types")
@RestController
@RequestMapping("/admin/item-types")
@RequiredArgsConstructor
public class ItemTypeAdminController {

    private final ItemTypeAdminService service;

    @Operation(summary = "Create an item type")
    @PostMapping
    public ResponseEntity<ItemTypeSummaryDto> create(@Valid @RequestBody ItemTypeCreateDto dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(dto));
    }

    @Operation(summary = "List all item types (paginated)")
    @GetMapping
    public ResponseEntity<Page<ItemTypeSummaryDto>> findAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return ResponseEntity.ok(service.findAll(PageRequest.of(page, size)));
    }

    @Operation(summary = "List item types by category")
    @GetMapping("/by-category/{categoryId}")
    public ResponseEntity<List<ItemTypeSummaryDto>> findByCategory(@PathVariable Integer categoryId) {
        return ResponseEntity.ok(service.findAllByCategoryId(categoryId));
    }

    @Operation(summary = "Bulk import item types")
    @PostMapping("/bulk")
    public ResponseEntity<BulkImportResult> bulkCreate(@RequestBody List<ItemTypeBulkDto> dtos) {
        return ResponseEntity.ok(service.bulkCreate(dtos));
    }

    @Operation(summary = "Export all item types")
    @GetMapping("/export")
    public ResponseEntity<List<ItemTypeBulkDto>> exportAll() {
        return ResponseEntity.ok(service.exportAll());
    }

    @Operation(summary = "Delete an item type")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Integer id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

}
