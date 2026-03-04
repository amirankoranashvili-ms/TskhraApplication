package com.tskhra.modulith.user_module.services;

import com.tskhra.modulith.user_module.exception.HttpConflictException;
import com.tskhra.modulith.user_module.exception.HttpNotFoundException;
import com.tskhra.modulith.user_module.model.domain.User;
import com.tskhra.modulith.user_module.model.enums.Gender;
import com.tskhra.modulith.user_module.model.enums.KycStatus;
import com.tskhra.modulith.user_module.model.enums.UserStatus;
import com.tskhra.modulith.user_module.model.requests.KeycloakSpiUserRegistrationDto;
import com.tskhra.modulith.user_module.model.requests.UserProfileUpdateDto;
import com.tskhra.modulith.user_module.model.requests.UserRegistrationRequestDto;
import com.tskhra.modulith.user_module.model.responses.UserProfileSelfDto;
import com.tskhra.modulith.user_module.model.responses.UserSelfDto;
import com.tskhra.modulith.user_module.repositories.UserRepository;
import jakarta.ws.rs.core.Response;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.keycloak.admin.client.Keycloak;
import org.keycloak.admin.client.resource.UsersResource;
import org.keycloak.representations.idm.CredentialRepresentation;
import org.keycloak.representations.idm.UserRepresentation;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class UserService {

    @Value("${keycloak.realm}") // todo propertiess!!
    private String realm;

    private final UserRepository userRepository;
    private final ImageService imageService;
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
                throw new HttpConflictException(response.readEntity(String.class)); // todo figure how to extract message
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

    public void registerKcUser(KeycloakSpiUserRegistrationDto dto) {
        LocalDateTime now = LocalDateTime.now();

        User user = User.builder()
                .username(dto.username())
                .email(dto.email())
                .keycloakId(UUID.fromString(dto.keycloakId()))
                .userStatus(UserStatus.ACTIVE)
                .kycStatus(KycStatus.NONE)
                .createdAt(now)
                .updatedAt(now)
                .build();

        userRepository.save(user);

    }

    public UserSelfDto currentUser(Jwt jwt) {
        String keycloakId = jwt.getClaimAsString("sub");
        User user = userRepository.findUserByKeycloakId(UUID.fromString(keycloakId))
                .orElseThrow(() -> new HttpNotFoundException("Current user not found."));

        return new UserSelfDto(
                user.getUsername(),
                user.getFirstName(),
                user.getLastName(),
                user.getEmail(),
                user.getKycStatus() == KycStatus.APPROVED,
                user.getProfilePictureUri() == null ?
                        "https://m.media-amazon.com/images/I/51P7JzxB6+L._SX679_.jpg" :
                        imageService.getAvatarUrl(user.getProfilePictureUri())
        );
    }

    public UserProfileSelfDto getCurrentUserProfile(Jwt jwt) {
        String keycloakId = jwt.getClaimAsString("sub");
        User user = userRepository.findUserByKeycloakId(UUID.fromString(keycloakId))
                .orElseThrow(() -> new HttpNotFoundException("Current user not found."));

        return new UserProfileSelfDto(
                user.getEmail(),
                user.getUsername(),
                user.getFirstName(),
                user.getLastName(),
                user.getKycStatus() == KycStatus.APPROVED,
                user.getCreatedAt().toLocalDate(),
                user.getPhoneNumber(),
                user.getGender() == null ? null : user.getGender().name(),
                user.getBirthDate(),
                user.getProfilePictureUri() == null ?
                        "https://m.media-amazon.com/images/I/51P7JzxB6+L._SX679_.jpg" :
                        imageService.getAvatarUrl(user.getProfilePictureUri())
        );
    }

    public void updateProfile(UserProfileUpdateDto dto, Jwt jwt) {
        String keycloakId = jwt.getClaimAsString("sub");
        User user = userRepository.findUserByKeycloakId(UUID.fromString(keycloakId))
                .orElseThrow(() -> new HttpNotFoundException("Current user not found."));

        user.setFirstName(dto.firstName());
        user.setLastName(dto.lastName());
        user.setGender(Gender.valueOf(dto.gender().toUpperCase()));
        user.setPhoneNumber(dto.phoneCountryCode() + dto.phoneNumber());
        user.setBirthDate(dto.birthDate());

        userRepository.save(user);
    }

    public void uploadAvatar(MultipartFile file, Jwt jwt) {
        String keycloakId = jwt.getClaimAsString("sub");
        User user = userRepository.findUserByKeycloakId(UUID.fromString(keycloakId))
                .orElseThrow(() -> new HttpNotFoundException("Current user not found."));

        String uri = imageService.uploadAvatar(file);
        user.setProfilePictureUri(uri);
        userRepository.save(user);
    }

    public void selfVerify(Jwt jwt) {
        setKycStatus(KycStatus.APPROVED, jwt);
    }

    public void selfUnverify(Jwt jwt) {
        setKycStatus(KycStatus.NONE, jwt);
    }

    private void setKycStatus(KycStatus status, Jwt jwt) {
        String keycloakId = jwt.getClaimAsString("sub");
        User user = userRepository.findUserByKeycloakId(UUID.fromString(keycloakId))
                .orElseThrow(() -> new HttpNotFoundException("Current user not found."));

        user.setKycStatus(status);
        userRepository.save(user);
    }
}
