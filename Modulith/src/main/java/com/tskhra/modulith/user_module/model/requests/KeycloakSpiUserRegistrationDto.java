package com.tskhra.modulith.user_module.model.requests;


public record KeycloakSpiUserRegistrationDto(
        String username,
        String email,
        String keycloakId
) {
}
