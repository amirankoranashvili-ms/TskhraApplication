package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.Category;
import com.tskhra.modulith.booking_module.model.enums.Lang;
import com.tskhra.modulith.booking_module.model.responses.CategoryDto;
import com.tskhra.modulith.booking_module.repositories.CategoryRepository;
import com.tskhra.modulith.common.properties.MinioProperties;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CategoryService {

    private final CategoryRepository categoryRepository;
    private final MinioProperties minioProperties;

    public List<CategoryDto> getCategoryTree(Lang lang) {
        return categoryRepository.findAllParentsWithChildren().stream()
                .map(c -> mapToDto(c, lang))
                .toList();
    }

    private CategoryDto mapToDto(Category c, Lang lang) {
        String name = switch (lang) {
            case KA -> c.getNameKa() == null ? c.getName() : c.getNameKa();
            case EN -> c.getName();
        };
        String iconUrl = c.getIconUri() == null ? null : minioProperties.externalUrl() + c.getIconUri();
        List<CategoryDto> subcategories = c.getChildren() == null ? List.of() :
                c.getChildren().stream()
                        .map(child -> mapToDto(child, lang))
                        .toList();
        return new CategoryDto(c.getId(), name, iconUrl, subcategories);
    }
}
