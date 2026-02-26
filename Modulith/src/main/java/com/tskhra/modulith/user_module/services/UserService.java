package com.tskhra.modulith.user_module.services;

import com.tskhra.modulith.user_module.exception.HttpConflictException;
import com.tskhra.modulith.user_module.model.domain.User;
import com.tskhra.modulith.user_module.model.enums.KycStatus;
import com.tskhra.modulith.user_module.model.enums.UserStatus;
import com.tskhra.modulith.user_module.model.requests.UserRegistrationRequestDto;
import com.tskhra.modulith.user_module.repositories.UserRepository;
import jakarta.ws.rs.core.Response;
import lombok.RequiredArgsConstructor;
import org.keycloak.admin.client.Keycloak;
import org.keycloak.admin.client.resource.UsersResource;
import org.keycloak.representations.idm.CredentialRepresentation;
import org.keycloak.representations.idm.UserRepresentation;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class UserService {

    @Value("${keycloak.realm}")
    private String realm;

    private final UserRepository userRepository;
    private final Keycloak keycloak;


    public void registerUser(UserRegistrationRequestDto dto) {
        if (userRepository.existsByUsername(dto.username())) {
            throw new HttpConflictException("Username Already Exists");
        }

        if (userRepository.existsByEmail(dto.email())) {
            throw new HttpConflictException("Email Already Exists");
        }

        UserRepresentation user = getUserRepresentation(dto);
        UsersResource usersResource = keycloak.realm(realm).users();

        try (Response response = usersResource.create(user)) {
            if (response.getStatus() == 201) {
                String userId = getCreatedId(response);
                LocalDateTime now = LocalDateTime.now();

                User createdUser = User.builder()
                        .username(dto.username())
                        .email(dto.email())
                        .keycloakId(UUID.fromString(userId))
                        .userStatus(UserStatus.ACTIVE)
                        .kycStatus(KycStatus.NONE)
                        .createdAt(now)
                        .updatedAt(now)
                        .build();

                userRepository.save(createdUser);

            } else if (response.getStatus() == 409) {
                throw new UserAlreadyExistsException(response.readEntity(String.class)); // todo figure how to extract message
            } else if (response.getStatus() == 400) {
                // todo handle
                throw new RuntimeException("Bad Request. Failed to register user.");
            } else {
                // todo handle
                throw new RuntimeException("Failed to register user. Status: " + response.getStatus());
            }
        }

    }

    private UserRepresentation getUserRepresentation(UserRegistrationRequestDto dto) {
        UserRepresentation user = new UserRepresentation();
        user.setUsername(dto.username());
        user.setEmail(dto.email());
        user.setEnabled(true);

        CredentialRepresentation credential = new CredentialRepresentation();
        credential.setType(CredentialRepresentation.PASSWORD);
        credential.setValue(dto.password());
        credential.setTemporary(false);

        user.setCredentials(Collections.singletonList(credential));
        return user;
    }

    private String getCreatedId(Response response) {
        String path = response.getLocation().getPath();
        return path.substring(path.lastIndexOf("/") + 1);
    }

}
