package com.tskhra.modulith.booking_module.repositories;

import com.tskhra.modulith.booking_module.model.domain.Booking;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface BookingRepository extends JpaRepository<Booking, Long> {
    List<Booking> getBookingsByBookingDate(LocalDate day);

    @Query("SELECT b FROM Booking b JOIN b.service s WHERE s.business.id = :id AND b.bookingDate = :day")
    List<Booking> getBusinessBookingsByDate(@Param("id") Long id, @Param("day") LocalDate day);
}
