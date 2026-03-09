package com.tskhra.modulith.booking_module.repositories;

import com.tskhra.modulith.booking_module.model.domain.Resource;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ResourceRepository extends JpaRepository<Resource, Long> {
    List<Resource> findByBusinessIdAndActivityStatus(Long businessId, ActivityStatus activityStatus);
}
