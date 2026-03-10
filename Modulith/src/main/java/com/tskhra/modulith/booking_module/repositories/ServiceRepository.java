package com.tskhra.modulith.booking_module.repositories;

import com.tskhra.modulith.booking_module.model.domain.Service;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

@Repository
public interface ServiceRepository extends JpaRepository<Service, Long> {
    List<Service> findByBusinessIdAndActivityStatus(Long businessId, ActivityStatus activityStatus);
    Optional<Service> findByIdAndActivityStatus(Long id, ActivityStatus activityStatus);

    List<Service> findByBusinessId(Long businessId);
}
