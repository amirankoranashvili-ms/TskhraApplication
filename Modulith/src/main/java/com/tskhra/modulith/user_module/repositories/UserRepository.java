package com.tskhra.modulith.user_module.repositories;

import com.tskhra.modulith.user_module.model.domain.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    boolean existsByUsername(String username);

    boolean existsByEmail(String email);

    Optional<User> findUserByKeycloakId(UUID keycloakId);
}
