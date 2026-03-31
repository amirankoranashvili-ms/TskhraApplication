package com.tskhra.modulith.booking_module.model.requests;

public record ServiceUpdateDto(
        String name,
        String nameKa,
        String description,
        String descriptionKa
) {
}
