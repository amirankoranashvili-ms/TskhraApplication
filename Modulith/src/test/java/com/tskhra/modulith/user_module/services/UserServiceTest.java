package com.tskhra.modulith.user_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.common.services.ImageService;
import com.tskhra.modulith.user_module.model.domain.User;
import com.tskhra.modulith.user_module.model.enums.KycStatus;
import com.tskhra.modulith.user_module.model.enums.UserStatus;
import com.tskhra.modulith.user_module.model.responses.UserSelfDto;
import com.tskhra.modulith.user_module.repositories.UserRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.oauth2.jwt.Jwt;

import java.time.Instant;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private ImageService imageService;

    @InjectMocks
    private UserService userService;

    @Test
    void getCurrentUserInfo_returnsDto_withAvatarAndVerified() {
        UUID keycloakId = UUID.randomUUID();
        Jwt jwt = buildJwt(keycloakId);

        User user = User.builder()
                .username("john")
                .firstName("John")
                .lastName("Doe")
                .email("john@example.com")
                .keycloakId(keycloakId)
                .kycStatus(KycStatus.APPROVED)
                .profilePictureUri("avatars/john.png")
                .createdAt(LocalDateTime.now())
                .build();

        when(userRepository.findUserByKeycloakId(keycloakId)).thenReturn(Optional.of(user));
        when(imageService.getAvatarUrl("avatars/john.png")).thenReturn("https://cdn.example.com/avatars/john.png");

        UserSelfDto result = userService.getCurrentUserInfo(jwt);

        assertEquals("john", result.userName());
        assertEquals("John", result.firstName());
        assertEquals("Doe", result.lastName());
        assertEquals("john@example.com", result.userEmail());
        assertTrue(result.isVerified());
        assertEquals("https://cdn.example.com/avatars/john.png", result.avatar());
    }

    @Test
    void getCurrentUserInfo_returnsNullAvatar_whenNoProfilePicture() {
        UUID keycloakId = UUID.randomUUID();
        Jwt jwt = buildJwt(keycloakId);

        User user = User.builder()
                .username("jane")
                .email("jane@example.com")
                .keycloakId(keycloakId)
                .kycStatus(KycStatus.NONE)
                .profilePictureUri(null)
                .createdAt(LocalDateTime.now())
                .build();

        when(userRepository.findUserByKeycloakId(keycloakId)).thenReturn(Optional.of(user));

        UserSelfDto result = userService.getCurrentUserInfo(jwt);

        assertNull(result.avatar());
        assertFalse(result.isVerified());
        verifyNoInteractions(imageService);
    }

    @Test
    void getUserNameById_returnsFirstName_whenPresent() {
        User user = User.builder().username("john123").firstName("John").build();
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        assertEquals("John", userService.getUserNameById(1L));
    }

    @Test
    void getUserNameById_fallsBackToUsername_whenFirstNameIsNull() {
        User user = User.builder().username("john123").firstName(null).build();
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));

        assertEquals("john123", userService.getUserNameById(1L));
    }

    @Test
    void getUserNameById_throwsNotFound_whenUserMissing() {
        when(userRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(HttpNotFoundException.class, () -> userService.getUserNameById(99L));
    }

    private Jwt buildJwt(UUID keycloakId) {
        return new Jwt(
                "token-value",
                Instant.now(),
                Instant.now().plusSeconds(300),
                Map.of("alg", "RS256"),
                Map.of("sub", keycloakId.toString())
        );
    }
}