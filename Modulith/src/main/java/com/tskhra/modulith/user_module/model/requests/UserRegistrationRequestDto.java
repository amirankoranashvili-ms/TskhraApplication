package com.tskhra.modulith.user_module.model.requests;

import com.tskhra.modulith.user_module.validation.ValidPassword;
import com.tskhra.modulith.user_module.validation.ValidUsername;
import jakarta.validation.constraints.Email;

// todo: validate username != password && email != password
public record UserRegistrationRequestDto(
        @ValidUsername
        String username,
        @Email
        String email,
        @ValidPassword
        String password
) {
}
