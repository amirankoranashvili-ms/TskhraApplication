package com.tskhra.modulith.notification_module.repositories;

import com.tskhra.modulith.notification_module.model.domain.FcmToken;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface FcmTokenRepository extends JpaRepository<FcmToken, Long> {

    List<FcmToken> findAllByUserId(Long userId);

    Optional<FcmToken> findByToken(String token);

    void deleteByToken(String token);
}
