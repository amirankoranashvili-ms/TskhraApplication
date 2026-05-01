package com.tskhra.modulith.user_module.model.responses;

import java.util.List;
import java.util.Set;

public record UserSelfDto(
        String userName,
        String userId,
        String firstName,
        String lastName,
        String userEmail,
        boolean isVerified,
        String avatar,
        Set<Long> favoriteBusinesses) {
}
