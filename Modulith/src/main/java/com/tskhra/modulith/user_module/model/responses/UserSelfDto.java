package com.tskhra.modulith.user_module.model.responses;

public record UserSelfDto(
        String userName,
        String firstName,
        String lastName,
        String userEmail,
        boolean isVerified
) {
}
