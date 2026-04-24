package com.tskhra.modulith.user_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpConflictException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.common.services.ImageService;
import com.tskhra.modulith.user_module.model.domain.User;
import com.tskhra.modulith.user_module.model.enums.Gender;
import com.tskhra.modulith.user_module.model.enums.KycStatus;
import com.tskhra.modulith.user_module.model.enums.UserStatus;
import com.tskhra.modulith.user_module.model.events.UserProfilePictureUpdatedEvent;
import com.tskhra.modulith.user_module.model.events.UserProfileUpdatedEvent;
import com.tskhra.modulith.user_module.model.events.UserRegisteredEvent;
import com.tskhra.modulith.user_module.model.requests.KeycloakSpiUserRegistrationDto;
import com.tskhra.modulith.user_module.model.requests.UserProfileUpdateDto;
import com.tskhra.modulith.user_module.model.requests.UserRegistrationRequestDto;
import com.tskhra.modulith.user_module.model.responses.UserProfileSelfDto;
import com.tskhra.modulith.user_module.model.responses.UserSelfDto;
import com.tskhra.modulith.user_module.repositories.UserRepository;
import jakarta.ws.rs.core.Response;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jspecify.annotations.NonNull;
import org.keycloak.admin.client.Keycloak;
import org.keycloak.admin.client.resource.UsersResource;
import org.keycloak.representations.idm.CredentialRepresentation;
import org.keycloak.representations.idm.ErrorRepresentation;
import org.keycloak.representations.idm.UserRepresentation;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.http.HttpStatus;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.modulith.NamedInterface;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
@NamedInterface
public class UserService {

    @Value("${keycloak.realm}") // todo propertiess!!
    private String realm;

    private final UserRepository userRepository;
    private final ImageService imageService;
    private final Keycloak keycloak;

    private final ApplicationEventPublisher events;
    private final SimpMessagingTemplate simpMessagingTemplate;


    @Transactional
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

                User saved = userRepository.save(createdUser);
                UserRegisteredEvent event = new UserRegisteredEvent(
                        UUID.randomUUID().toString(),
                        now,
                        "user_registered",
                        userId,
                        new UserRegisteredEvent.Payload(
                                userId,
                                user.getUsername(),
                                user.getEmail()
                        )
                );

//                events.publishEvent(event);
                simpMessagingTemplate.convertAndSend("/topic/users", "User " + saved.getUsername() + " has registered");

            } else if (response.getStatus() == 409) {
                ErrorRepresentation error = response.readEntity(ErrorRepresentation.class);
                String errorMessage = error.getErrorMessage();
                throw new HttpConflictException(errorMessage);
            } else if (response.getStatus() == 400) {
                ErrorRepresentation error = response.readEntity(ErrorRepresentation.class);
                String errorMessage = error.getErrorMessage();
                throw new HttpBadRequestException(errorMessage);
            } else {
                ErrorRepresentation error = response.readEntity(ErrorRepresentation.class);
                String errorMessage = error.getErrorMessage();
                throw new HttpException(errorMessage, HttpStatus.valueOf(response.getStatus()));
            }
        }

    }

    @Transactional
    public void registerKcUser(KeycloakSpiUserRegistrationDto dto) {
        log.info("registerKcUser: start for username={}", dto.username());
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

        String userId = userRepository.save(user).getKeycloakId().toString();
        log.info("registerKcUser: user saved with keycloakId={}", userId);

        UserRegisteredEvent event = new UserRegisteredEvent(
                UUID.randomUUID().toString(),
                now,
                "user_registered",
                userId,
                new UserRegisteredEvent.Payload(
                        userId,
                        user.getUsername(),
                        user.getEmail()
                ));

        log.info("registerKcUser: publishing UserRegisteredEvent for keycloakId={}", userId);
//        events.publishEvent(event);
        log.info("registerKcUser: event published successfully for keycloakId={}", userId);
    }

    public UserSelfDto getCurrentUserInfo(Jwt jwt) {
        User user = getCurrentUser(jwt);

        return new UserSelfDto(
                user.getUsername(),
                user.getFirstName(),
                user.getLastName(),
                user.getEmail(),
                user.getKycStatus() == KycStatus.APPROVED,
                user.getProfilePictureUri() == null ?
                        null :
                        imageService.getAvatarUrl(user.getProfilePictureUri()),
                user.getFavoriteBusinessIds()
        );
    }

    public UserProfileSelfDto getCurrentUserProfile(Jwt jwt) {
        User user = getCurrentUser(jwt);

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
                        null :
                        imageService.getAvatarUrl(user.getProfilePictureUri())
        );
    }

    @Transactional
    public void updateProfile(UserProfileUpdateDto dto, Jwt jwt) {
        User user = getCurrentUser(jwt);

        user.setFirstName(dto.firstName());
        user.setLastName(dto.lastName());
        user.setGender(Gender.valueOf(dto.gender().toUpperCase()));
        user.setPhoneNumber(dto.phoneCountryCode() + dto.phoneNumber());
        user.setBirthDate(dto.birthDate());

        userRepository.save(user);

        String userId = jwt.getClaimAsString("sub");
//        events.publishEvent(new UserProfileUpdatedEvent(
//                UUID.randomUUID().toString(),
//                LocalDateTime.now(),
//                "user_profile_updated",
//                userId,
//                new UserProfileUpdatedEvent.Payload(
//                        userId,
//                        dto.firstName(),
//                        dto.lastName(),
//                        dto.gender(),
//                        dto.birthDate().toString(),
//                        dto.phoneCountryCode() + dto.phoneNumber()
//                )
//        ));
    }

    @Transactional
    public void uploadAvatar(MultipartFile file, Jwt jwt) {
        User user = getCurrentUser(jwt);

        String uri = imageService.uploadAvatar(file);
        user.setProfilePictureUri(uri);
        userRepository.save(user);

        String userId = jwt.getClaimAsString("sub");
//        events.publishEvent(new UserProfilePictureUpdatedEvent(
//                UUID.randomUUID().toString(),
//                LocalDateTime.now(),
//                "user_profile_picture_updated",
//                userId,
//                new UserProfilePictureUpdatedEvent.Payload(
//                        userId,
//                        uri
//                )
//        ));
    }

    public void deleteAvatar(Jwt jwt) {
        User user = getCurrentUser(jwt);

        user.setProfilePictureUri(null);
        userRepository.save(user);
    }

    public void selfVerify(Jwt jwt) {
        setKycStatus(KycStatus.APPROVED, jwt);
    }

    public void selfUnverify(Jwt jwt) {
        setKycStatus(KycStatus.NONE, jwt);
    }


    //    Helper methods
    private void setKycStatus(KycStatus status, Jwt jwt) {
        User user = getCurrentUser(jwt);

        user.setKycStatus(status);
        userRepository.save(user);
    }

    public @NonNull User getCurrentUser(Jwt jwt) {
        String keycloakId = jwt.getClaimAsString("sub");
        return userRepository.findUserByKeycloakId(UUID.fromString(keycloakId))
                .orElseThrow(() -> new HttpNotFoundException("Current user not found."));
    }

    private String getCreatedId(Response response) {
        String path = response.getLocation().getPath();
        return path.substring(path.lastIndexOf("/") + 1);
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

    public String getUserNameById(Long userId) {
        User user = userRepository.findById(userId).orElseThrow(
                () -> new HttpNotFoundException("User not found")
        );

        return user.getFirstName() == null ? user.getUsername() : user.getFirstName();
    }

    public void favoriteBusiness(Long businessId, Jwt jwt) {
        User user = getCurrentUser(jwt);
        user.addFavoriteBusiness(businessId);
        userRepository.save(user);
    }

    public void unfavoriteBusiness(Long businessId, Jwt jwt) {
        User user = getCurrentUser(jwt);
        user.removeFavoriteBusiness(businessId);
        userRepository.save(user);
    }

    public String getUserKeycloakIdById(Long userId) {
        User user = userRepository.findById(userId).orElseThrow(
                () -> new HttpNotFoundException("User not found")
        );
        return user.getKeycloakId().toString();
    }
}
