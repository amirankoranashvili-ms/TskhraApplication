package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.requests.BrandCreateDto;
import com.tskhra.modulith.trade_module.model.responses.BrandSummaryDto;
import com.tskhra.modulith.trade_module.services.BrandAdminService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "Brands", description = "Manage and browse brands")
@RestController
@RequiredArgsConstructor
public class BrandController {

    private final BrandAdminService service;

    @Operation(summary = "List all brands")
    @GetMapping("/brands")
    public ResponseEntity<List<BrandSummaryDto>> findAll() {
        return ResponseEntity.ok(service.findAll());
    }

    @Operation(summary = "Create a brand")
    @PostMapping("/admin/brands")
    public ResponseEntity<BrandSummaryDto> create(@Valid @RequestBody BrandCreateDto dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(dto));
    }

    @Operation(summary = "Delete a brand")
    @DeleteMapping("/admin/brands/{id}")
    public ResponseEntity<Void> delete(@PathVariable Integer id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

}
