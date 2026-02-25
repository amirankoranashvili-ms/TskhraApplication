package com.tskhra.modulith.user_module.repositories;

import com.tskhra.modulith.user_module.model.domain.UserVerificationRequest;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserVerificationRequestRepository extends JpaRepository<UserVerificationRequest, Long> {
}
