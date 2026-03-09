package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.Booking;
import com.tskhra.modulith.booking_module.model.domain.Business;
import com.tskhra.modulith.booking_module.model.domain.Resource;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import com.tskhra.modulith.booking_module.model.enums.BookingStatus;
import com.tskhra.modulith.booking_module.model.requests.IndividualBookingRequest;
import com.tskhra.modulith.booking_module.repositories.BookingRepository;
import com.tskhra.modulith.booking_module.repositories.BusinessRepository;
import com.tskhra.modulith.booking_module.repositories.ResourceRepository;
import com.tskhra.modulith.booking_module.repositories.ServiceRepository;
import com.tskhra.modulith.common.exception.HttpConflictException;
import com.tskhra.modulith.common.exception.HttpForbiddenError;
import com.tskhra.modulith.common.exception.HttpNotFoundException;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import com.tskhra.modulith.booking_module.model.domain.Service;

import java.util.Objects;

@org.springframework.stereotype.Service
@RequiredArgsConstructor
public class BookingService {

    private final BookingRepository bookingRepository;
    private final ServiceRepository serviceRepository;
    private final BusinessRepository businessRepository;
    private final ResourceRepository resourceRepository;

    private final UserService userService;


    public void createBooking(IndividualBookingRequest request, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Service service = serviceRepository.findById(Long.valueOf(request.serviceId())).orElseThrow(
                () -> new HttpNotFoundException("Service not found")
        );
        Business business = businessRepository.findById(service.getBusiness().getId()).orElseThrow(
                () -> new HttpNotFoundException("Business not found")
        );

        if (!isTimeAvailable(request)) {
            throw new HttpNotFoundException("Time slot not available");
        }

        Resource res = null;
        if (business.getResources() == null || business.getResources().isEmpty()) {
            Resource resource = new Resource();
            resource.setBusiness(business);
            resource.setName("self");
            resource.setActivityStatus(ActivityStatus.ACTIVE);
            res = resourceRepository.save(resource);
        } else {
            res = business.getResources().getFirst();
        }

        Booking booking = Booking.builder()
                .userId(userId)
                .service(service)
                .resource(res)
                .bookingDate(request.date())
                .startTime(request.startTime())
                .duration(service.getSessionDuration())
                .bookingStatus(BookingStatus.AWAITING)
                .totalPrice(service.getSessionPrice())
                .build();

        bookingRepository.save(booking);
    }

    private boolean isTimeAvailable(IndividualBookingRequest request) {
        return true;
    }

    public void approveRequest(Long bookingId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Booking booking = bookingRepository.findById(bookingId).orElseThrow(
                () -> new HttpNotFoundException("Booking not found")
        );

        Service service = booking.getService();
        Business business = service.getBusiness();
        if (!Objects.equals(business.getUserId(), userId)) {
            throw new HttpForbiddenError("You are not authorized to approve this request");
        }

        if (booking.getBookingStatus() != BookingStatus.AWAITING) {
            throw new HttpConflictException("Booking is not in AWAITING status");
        }

        booking.setBookingStatus(BookingStatus.SCHEDULED);
        bookingRepository.save(booking);
    }

    public void rejectRequest(Long bookingId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Booking booking = bookingRepository.findById(bookingId).orElseThrow(
                () -> new HttpNotFoundException("Booking not found")
        );

        Service service = booking.getService();
        Business business = service.getBusiness();
        if (!Objects.equals(business.getUserId(), userId)) {
            throw new HttpForbiddenError("You are not authorized to reject this request");
        }

        if (booking.getBookingStatus() != BookingStatus.AWAITING) {
            throw new HttpConflictException("Booking is not in AWAITING status");
        }

        booking.setBookingStatus(BookingStatus.REJECTED);
        bookingRepository.save(booking);
    }
}
