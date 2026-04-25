package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.requests.TradeCategoryBulkDto;
import com.tskhra.modulith.trade_module.model.requests.TradeCategoryCreateDto;
import com.tskhra.modulith.trade_module.model.responses.BulkImportResult;
import com.tskhra.modulith.trade_module.model.responses.TradeCategorySummaryDto;
import com.tskhra.modulith.trade_module.services.TradeCategoryAdminService;
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

@Tag(name = "Trade Category Admin", description = "Manage trade categories")
@RestController
@RequestMapping("/admin/trade-categories")
@RequiredArgsConstructor
public class TradeCategoryAdminController {

    private final TradeCategoryAdminService service;

    @Operation(summary = "Create a trade category")
    @PostMapping
    public ResponseEntity<TradeCategorySummaryDto> create(@Valid @RequestBody TradeCategoryCreateDto dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(dto));
    }

    @Operation(summary = "List all categories (paginated)")
    @GetMapping
    public ResponseEntity<Page<TradeCategorySummaryDto>> listAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return ResponseEntity.ok(service.findAll(PageRequest.of(page, size)));
    }

    @Operation(summary = "List children of a category")
    @GetMapping("/{id}/children")
    public ResponseEntity<List<TradeCategorySummaryDto>> listChildren(@PathVariable Integer id) {
        return ResponseEntity.ok(service.findChildren(id));
    }

    @Operation(summary = "Bulk import categories")
    @PostMapping("/bulk")
    public ResponseEntity<BulkImportResult> bulkCreate(@RequestBody List<TradeCategoryBulkDto> dtos) {
        return ResponseEntity.ok(service.bulkCreate(dtos));
    }

    @Operation(summary = "Export all categories")
    @GetMapping("/export")
    public ResponseEntity<List<TradeCategoryBulkDto>> exportAll() {
        return ResponseEntity.ok(service.exportAll());
    }

    @Operation(summary = "Delete a trade category")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Integer id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

}
