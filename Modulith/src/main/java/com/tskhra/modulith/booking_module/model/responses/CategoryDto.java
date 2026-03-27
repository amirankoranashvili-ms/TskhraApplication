package com.tskhra.modulith.booking_module.model.responses;

import java.util.List;

public record CategoryDto(
        Long id,
        String name,
        String iconUrl,
        List<CategoryDto> subcategories
) {
}
