package com.tskhra.modulith.booking_module.repositories;

import com.tskhra.modulith.booking_module.model.domain.BusinessUnavailableSchedule;
import com.tskhra.modulith.booking_module.model.enums.WeekDay;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface BusinessUnavailableScheduleRepository extends JpaRepository<BusinessUnavailableSchedule, Long> {
    List<BusinessUnavailableSchedule> findByBusinessIdAndIntervalWeekDay(Long businessId, WeekDay weekDay);
}
