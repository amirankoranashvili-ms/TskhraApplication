package com.tskhra.modulith.user_module.model.requests;

import com.tskhra.modulith.user_module.validation.MaxAge;
import com.tskhra.modulith.user_module.validation.MinAge;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import java.time.LocalDate;

public record UserProfileUpdateDto (
        @NotBlank(message = "First name cannot be blank")
        @Size(min = 2, max = 50, message = "First name must be between 2 and 50 characters")
        String firstName,

        @NotBlank(message = "Last name cannot be blank")
        @Size(min = 2, max = 50, message = "Last name must be between 2 and 50 characters")
        String lastName,

        @NotBlank(message = "Gender cannot be blank")
        @Pattern(regexp = "(?i)^(male|female)$", message = "Gender must be 'male' or 'female'")
        String gender,

        @NotNull(message = "Birth date is required")
        @MinAge(value = 16, message = "User must be at least 16 years old")
        @MaxAge(value = 100, message = "User is too old!")
        LocalDate birthDate,

        @NotBlank(message = "Country code cannot be blank")
        @Pattern(regexp = "^\\+995$", message = "Country code must be +995") // future "^\\+(995|999|123)$"
        String phoneCountryCode,

        @NotBlank(message = "Phone number cannot be blank")
        @Pattern(regexp = "^5\\d{8}$", message = "Phone number must be 9 digits long and start with 5")
        String phoneNumber
) {
}
