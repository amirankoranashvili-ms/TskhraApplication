package com.tskhra.modulith.booking_module.repositories;

import com.tskhra.modulith.booking_module.model.domain.Booking;
import com.tskhra.modulith.booking_module.model.enums.BookingStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
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

    @Query("SELECT b FROM Booking b JOIN b.service s WHERE s.business.id = :businessId AND b.bookingDate = :date AND b.bookingStatus IN :statuses")
    List<Booking> findByBusinessIdAndDateAndStatuses(@Param("businessId") Long businessId, @Param("date") LocalDate date, @Param("statuses") List<BookingStatus> statuses);

    List<Booking> findAllByService_IdAndBookingStatus(Long serviceId, BookingStatus bookingStatus);

    List<Booking> findAllByServiceId(Long id);

    List<Booking> findAllByUserId(Long userId);

    @Query("SELECT b FROM Booking b WHERE b.userId = :userId AND b.bookingStatus IN :statuses")
    Page<Booking> findAllActiveByUserId(Long userId, Pageable pageable, List<BookingStatus> statuses);

    @Query("SELECT COUNT(b) FROM Booking b WHERE b.service.business.id IN :businessIds AND b.bookingStatus = :status")
    int countByBusinessIdsAndStatus(@Param("businessIds") List<Long> businessIds, @Param("status") BookingStatus status);

    @Query(value = "SELECT pg_advisory_xact_lock(CAST(:businessId AS integer), CAST(EXTRACT(EPOCH FROM CAST(:date AS date)) / 86400 AS integer))", nativeQuery = true)
    void lockBusinessDate(@Param("businessId") Long businessId, @Param("date") LocalDate date);

    @Query("SELECT COUNT(b) > 0 FROM Booking b JOIN b.service s " +
            "WHERE s.business.id = :businessId AND b.bookingDate = :date " +
            "AND b.bookingStatus IN :statuses " +
            "AND b.startTime < :endTime AND (b.startTime + b.duration) > :startTime")
    boolean existsOverlappingBooking(@Param("businessId") Long businessId,
                                     @Param("date") LocalDate date,
                                     @Param("statuses") List<BookingStatus> statuses,
                                     @Param("startTime") int startTime,
                                     @Param("endTime") int endTime);

    @Query("SELECT b FROM Booking b WHERE b.service.business.id = :businessId AND b.bookingStatus = :bookingStatus")
    List<Booking> findByBusinessIdAndStatus(@Param("businessId") Long businessId, @Param("bookingStatus") BookingStatus bookingStatus);
}
