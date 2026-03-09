package com.tskhra.modulith.booking_module.repositories;

import com.tskhra.modulith.booking_module.model.domain.BusinessUnavailableOnetime;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface BusinessUnavailableOnetimeRepository extends JpaRepository<BusinessUnavailableOnetime, Long> {
    List<BusinessUnavailableOnetime> findByBusinessIdAndDate(Long businessId, LocalDate date);
}
