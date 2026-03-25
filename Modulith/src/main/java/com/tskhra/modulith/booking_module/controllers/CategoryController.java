package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.responses.MainCategoryDto;
import com.tskhra.modulith.booking_module.services.CategoryService;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/categories")
@RequiredArgsConstructor
public class CategoryController {

    private final CategoryService categoryService;

    @Operation(summary = "Get full category tree")
    @GetMapping
    public ResponseEntity<Map<String, List<String>>> getAll() {
        Map<String, List<String>> categoryTree = categoryService.getCategoryTree();
        return ResponseEntity.status(HttpStatus.OK).body(categoryTree);
    }

    @Operation(summary = "List top-level categories")
    @GetMapping("/main")
    public ResponseEntity<List<MainCategoryDto>> getMainCategories() {
        List<MainCategoryDto> mainCategories = categoryService.getMainCategories();
        return ResponseEntity.status(HttpStatus.OK).body(mainCategories);
    }

}
