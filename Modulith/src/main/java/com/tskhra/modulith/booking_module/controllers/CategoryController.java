package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.services.CategoryService;
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

    @GetMapping
    public ResponseEntity<Map<String, List<String>>> getAll() {
        Map<String, List<String>> categoryTree = categoryService.getCategoryTree();
        return ResponseEntity.status(HttpStatus.OK).body(categoryTree);
    }

    @GetMapping("/main")
    public ResponseEntity<List<String>> getMainCategories() {
        List<String> mainCategories = categoryService.getMainCategories();
        return ResponseEntity.status(HttpStatus.OK).body(mainCategories);
    }

}
