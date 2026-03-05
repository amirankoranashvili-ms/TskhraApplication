package com.tskhra.modulith.booking_module.repositories;

import com.tskhra.modulith.booking_module.model.domain.BusinessUnavailableSchedule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface BusinessUnavailableScheduleRepository extends JpaRepository<BusinessUnavailableSchedule, Long> {
}
