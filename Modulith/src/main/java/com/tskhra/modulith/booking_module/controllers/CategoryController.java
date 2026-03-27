package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.enums.Lang;
import com.tskhra.modulith.booking_module.model.responses.CategoryDto;
import com.tskhra.modulith.booking_module.services.CategoryService;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/categories")
@RequiredArgsConstructor
public class CategoryController {

    private final CategoryService categoryService;

    @Operation(summary = "Get full category tree")
    @GetMapping
    public ResponseEntity<List<CategoryDto>> getAll(@RequestParam(defaultValue = "EN") Lang lang) {
        List<CategoryDto> categoryTree = categoryService.getCategoryTree(lang);
        return ResponseEntity.status(HttpStatus.OK).body(categoryTree);
    }

}
