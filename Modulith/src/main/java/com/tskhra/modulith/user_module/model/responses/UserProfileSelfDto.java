package com.tskhra.modulith.user_module.model.responses;

import java.time.LocalDate;

public record UserProfileSelfDto(
        String userEmail,
        String userName,
        String firstName,
        String lastName,
        Boolean status,
        LocalDate createDate,
        String phoneNumber,
        String gender,
        LocalDate birthDate,

        String avatar
) {
}
