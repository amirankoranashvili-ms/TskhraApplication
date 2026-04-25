package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.requests.TradeCategoryCreateDto;
import com.tskhra.modulith.trade_module.model.responses.TradeCategorySummaryDto;
import com.tskhra.modulith.trade_module.services.TradeCategoryAdminService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
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

    @Operation(summary = "List all root categories")
    @GetMapping
    public ResponseEntity<List<TradeCategorySummaryDto>> listParents() {
        return ResponseEntity.ok(service.findAllParents());
    }

    @Operation(summary = "List children of a category")
    @GetMapping("/{id}/children")
    public ResponseEntity<List<TradeCategorySummaryDto>> listChildren(@PathVariable Integer id) {
        return ResponseEntity.ok(service.findChildren(id));
    }

    @Operation(summary = "Delete a trade category")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Integer id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

}
