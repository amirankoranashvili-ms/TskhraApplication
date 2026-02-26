package com.tskhra.modulith.user_module.model.requests;

public record UserRegistrationRequestDto(
        String username,
        String email,
        String password
) {
}
