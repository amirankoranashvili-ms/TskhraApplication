package com.tskhra.modulith.booking_module.model.requests;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import org.hibernate.validator.constraints.URL;

public record Info(
        @NotBlank(message = "Phone number is required")
        @Pattern(
                regexp = "^(5\\d{8}|\\+9955\\d{8})$",
                message = "Phone number must be 9 digits starting with 5, or 13 characters starting with +9955"
        )
        String phoneNumber,
        @URL(message = "Invalid URL format")
        String instagramUrl,
        @URL(message = "Invalid URL format")
        String facebookUrl
) {
}
