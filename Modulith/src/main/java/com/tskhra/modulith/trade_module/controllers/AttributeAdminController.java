package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.requests.AttributeCreateDto;
import com.tskhra.modulith.trade_module.model.responses.AttributeSummaryDto;
import com.tskhra.modulith.trade_module.model.responses.BulkImportResult;
import com.tskhra.modulith.trade_module.services.AttributeAdminService;
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

@Tag(name = "Attribute Admin", description = "Manage item attributes")
@RestController
@RequestMapping("/admin/attributes")
@RequiredArgsConstructor
public class AttributeAdminController {

    private final AttributeAdminService service;

    @Operation(summary = "Create an attribute")
    @PostMapping
    public ResponseEntity<AttributeSummaryDto> create(@Valid @RequestBody AttributeCreateDto dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(dto));
    }

    @Operation(summary = "List all attributes (paginated)")
    @GetMapping
    public ResponseEntity<Page<AttributeSummaryDto>> findAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return ResponseEntity.ok(service.findAll(PageRequest.of(page, size)));
    }

    @Operation(summary = "Bulk import attributes")
    @PostMapping("/bulk")
    public ResponseEntity<BulkImportResult> bulkCreate(@RequestBody List<AttributeCreateDto> dtos) {
        return ResponseEntity.ok(service.bulkCreate(dtos));
    }

    @Operation(summary = "Export all attributes")
    @GetMapping("/export")
    public ResponseEntity<List<AttributeCreateDto>> exportAll() {
        return ResponseEntity.ok(service.exportAll());
    }

    @Operation(summary = "Delete an attribute")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Integer id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

}
