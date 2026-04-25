package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.requests.BrandCreateDto;
import com.tskhra.modulith.trade_module.model.responses.BrandSummaryDto;
import com.tskhra.modulith.trade_module.model.responses.BulkImportResult;
import com.tskhra.modulith.trade_module.services.BrandAdminService;
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

@Tag(name = "Brands", description = "Manage and browse brands")
@RestController
@RequiredArgsConstructor
public class BrandController {

    private final BrandAdminService service;

    @Operation(summary = "List all brands (paginated)")
    @GetMapping("/brands")
    public ResponseEntity<Page<BrandSummaryDto>> findAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return ResponseEntity.ok(service.findAll(PageRequest.of(page, size)));
    }

    @Operation(summary = "Create a brand")
    @PostMapping("/admin/brands")
    public ResponseEntity<BrandSummaryDto> create(@Valid @RequestBody BrandCreateDto dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(dto));
    }

    @Operation(summary = "Bulk import brands")
    @PostMapping("/admin/brands/bulk")
    public ResponseEntity<BulkImportResult> bulkCreate(@RequestBody List<BrandCreateDto> dtos) {
        return ResponseEntity.ok(service.bulkCreate(dtos));
    }

    @Operation(summary = "Export all brands")
    @GetMapping("/admin/brands/export")
    public ResponseEntity<List<BrandCreateDto>> exportAll() {
        return ResponseEntity.ok(service.exportAll());
    }

    @Operation(summary = "Delete a brand")
    @DeleteMapping("/admin/brands/{id}")
    public ResponseEntity<Void> delete(@PathVariable Integer id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

}
