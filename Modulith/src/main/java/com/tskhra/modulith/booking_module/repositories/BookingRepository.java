package com.tskhra.modulith.booking_module.repositories;

import com.tskhra.modulith.booking_module.model.domain.Booking;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface BookingRepository extends JpaRepository<Booking, Long> {
}
