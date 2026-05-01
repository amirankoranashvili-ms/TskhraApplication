package com.tskhra.modulith.booking_module.repositories;

import com.tskhra.modulith.booking_module.model.domain.BusinessChatbot;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface BusinessChatbotRepository extends JpaRepository<BusinessChatbot, Long> {
    Optional<BusinessChatbot> findByBusinessId(Long businessId);
}
