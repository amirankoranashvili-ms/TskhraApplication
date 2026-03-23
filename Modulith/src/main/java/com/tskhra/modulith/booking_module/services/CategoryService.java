package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.Category;
import com.tskhra.modulith.booking_module.repositories.CategoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class CategoryService {

    private final CategoryRepository categoryRepository;

    public Map<String, List<String>> getCategoryTree() { // todo maybe refactor to not call db many times
        return categoryRepository.findAll().stream()
                .filter(category -> category.getParent() == null)
                .collect(Collectors.toMap(
                        Category::getName,
                        category -> category.getChildren().stream()
                                .map(Category::getName)
                                .toList()
                ));
    }

    public List<String> getMainCategories() {
        return categoryRepository.findAll().stream()
                .filter(c -> c.getParent() == null)
                .map(Category::getName)
                .toList();
    }
}
