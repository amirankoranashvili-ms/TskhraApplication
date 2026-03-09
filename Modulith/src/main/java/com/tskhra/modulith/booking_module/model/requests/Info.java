package com.tskhra.modulith.booking_module.model.requests;

import org.hibernate.validator.constraints.URL;

public record Info(
        String phoneNumber,
        @URL(message = "Invalid URL format")
        String instagramUrl,
        @URL(message = "Invalid URL format")
        String facebookUrl
) {
}
