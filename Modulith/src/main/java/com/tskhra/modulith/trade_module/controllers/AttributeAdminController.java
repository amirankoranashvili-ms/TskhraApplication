package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.requests.AttributeCreateDto;
import com.tskhra.modulith.trade_module.model.responses.AttributeSummaryDto;
import com.tskhra.modulith.trade_module.services.AttributeAdminService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
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

    @Operation(summary = "List all attributes")
    @GetMapping
    public ResponseEntity<List<AttributeSummaryDto>> findAll() {
        return ResponseEntity.ok(service.findAll());
    }

    @Operation(summary = "Delete an attribute")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Integer id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

}
