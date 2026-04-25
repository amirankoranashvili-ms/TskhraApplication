package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.requests.ItemTypeCreateDto;
import com.tskhra.modulith.trade_module.model.responses.ItemTypeSummaryDto;
import com.tskhra.modulith.trade_module.services.ItemTypeAdminService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
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

    @Operation(summary = "List all item types")
    @GetMapping
    public ResponseEntity<List<ItemTypeSummaryDto>> findAll() {
        return ResponseEntity.ok(service.findAll());
    }

    @Operation(summary = "List item types by category")
    @GetMapping("/by-category/{categoryId}")
    public ResponseEntity<List<ItemTypeSummaryDto>> findByCategory(@PathVariable Integer categoryId) {
        return ResponseEntity.ok(service.findAllByCategoryId(categoryId));
    }

    @Operation(summary = "Delete an item type")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Integer id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

}
