package com.tskhra.modulith.booking_module.repositories;

import com.tskhra.modulith.booking_module.model.domain.Business;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface BusinessRepository extends JpaRepository<Business, Long> {
    List<Business> findByUserId(Long userId);
    long countByUserId(Long userId);

    List<Business> findByUserIdAndActivityStatus(Long userId, ActivityStatus activityStatus);
    long countByUserIdAndActivityStatus(Long userId, ActivityStatus activityStatus);
    Page<Business> findAllByActivityStatus(ActivityStatus activityStatus, Pageable pageable);
    Optional<Business> findByIdAndActivityStatus(Long id, ActivityStatus activityStatus);

    Page<Business> findAllByActivityStatusAndCategoryId(ActivityStatus activityStatus, Long categoryId, Pageable pageable);
}
