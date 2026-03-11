package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.*;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import com.tskhra.modulith.booking_module.model.enums.BookingStatus;
import com.tskhra.modulith.booking_module.model.enums.BusinessType;
import com.tskhra.modulith.booking_module.model.enums.WeekDay;
import com.tskhra.modulith.booking_module.model.requests.IndividualBookingRequest;
import com.tskhra.modulith.booking_module.model.responses.BookingDto;
import com.tskhra.modulith.booking_module.repositories.*;
import com.tskhra.modulith.common.exception.HttpBadRequestException;
import com.tskhra.modulith.common.exception.HttpConflictException;
import com.tskhra.modulith.common.exception.HttpForbiddenError;
import com.tskhra.modulith.common.exception.HttpNotFoundException;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.transaction.annotation.Transactional;
import com.tskhra.modulith.booking_module.model.domain.Service;

import java.time.LocalDate;
import java.util.List;
import java.util.Objects;

@org.springframework.stereotype.Service
@RequiredArgsConstructor
public class BookingService {

    private final BookingRepository bookingRepository;
    private final ServiceRepository serviceRepository;
    private final BusinessRepository businessRepository;
    private final ResourceRepository resourceRepository;
    private final BusinessScheduleRepository businessScheduleRepository;
    private final BusinessUnavailableScheduleRepository businessUnavailableScheduleRepository;
    private final BusinessUnavailableOnetimeRepository businessUnavailableOnetimeRepository;

    private final UserService userService;


    @Transactional
    public void createBooking(IndividualBookingRequest request, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Service service = serviceRepository.findByIdAndActivityStatus(Long.valueOf(request.serviceId()), ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Service not found")
        );
        Business business = businessRepository.findByIdAndActivityStatus(service.getBusiness().getId(), ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Business not found")
        );

        if (business.getBusinessType() != BusinessType.INDIVIDUAL) {
            throw new HttpBadRequestException("This booking flow is only for INDIVIDUAL businesses");
        }

        if (request.date().isBefore(LocalDate.now())) {
            throw new HttpBadRequestException("Booking date cannot be in the past");
        }

        int endTime = request.startTime() + service.getSessionDuration();
        if (!isTimeAvailable(business.getId(), request.date(), request.startTime(), endTime)) {
            throw new HttpConflictException("Time slot not available");
        }

        List<Resource> activeResources = resourceRepository.findByBusinessIdAndActivityStatus(business.getId(), ActivityStatus.ACTIVE);
        Resource res;
        if (activeResources.isEmpty()) {
            Resource resource = new Resource();
            resource.setBusiness(business);
            resource.setName("self");
            resource.setActivityStatus(ActivityStatus.ACTIVE);
            res = resourceRepository.save(resource);
        } else {
            res = activeResources.getFirst();
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

    private boolean isTimeAvailable(Long businessId, LocalDate date, int startTime, int endTime) {
        WeekDay weekDay = WeekDay.from(date.getDayOfWeek());

        List<BusinessSchedule> schedules = businessScheduleRepository.findByBusinessIdAndIntervalWeekDay(businessId, weekDay);
        boolean withinSchedule = schedules.stream().anyMatch(s ->
                s.getInterval().getStartTime() <= startTime && endTime <= s.getInterval().getEndTime()
        );
        if (!withinSchedule) {
            return false;
        }

        List<BusinessUnavailableSchedule> unavailableSchedules = businessUnavailableScheduleRepository.findByBusinessIdAndIntervalWeekDay(businessId, weekDay);
        boolean overlapsUnavailable = unavailableSchedules.stream().anyMatch(u ->
                startTime < u.getInterval().getEndTime() && u.getInterval().getStartTime() < endTime
        );
        if (overlapsUnavailable) {
            return false;
        }

        List<BusinessUnavailableOnetime> onetimes = businessUnavailableOnetimeRepository.findByBusinessIdAndDate(businessId, date);
        boolean overlapsOnetime = onetimes.stream().anyMatch(o ->
                startTime < o.getEndTime() && o.getStartTime() < endTime
        );
        if (overlapsOnetime) {
            return false;
        }

        List<Booking> existingBookings = bookingRepository.findByBusinessIdAndDateAndStatuses(
                businessId, date, List.of(BookingStatus.AWAITING, BookingStatus.SCHEDULED)
        );
        boolean overlapsBooking = existingBookings.stream().anyMatch(b ->
                startTime < (b.getStartTime() + b.getDuration()) && b.getStartTime() < endTime
        );
        return !overlapsBooking;
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

    public void cancelByBusiness(Long bookingId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Booking booking = bookingRepository.findById(bookingId).orElseThrow(
                () -> new HttpNotFoundException("Booking not found")
        );

        Service service = booking.getService();
        Business business = service.getBusiness();
        if (!Objects.equals(business.getUserId(), userId)) {
            throw new HttpForbiddenError("You are not authorized to cancel this request");
        }

        if (booking.getBookingStatus() != BookingStatus.SCHEDULED) {
            throw new HttpConflictException("Booking is not Scheduled");
        }

        booking.setBookingStatus(BookingStatus.CANCELLED_BY_BUSINESS);
        bookingRepository.save(booking);
    }

    public void cancelByUser(Long bookingId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Booking booking = bookingRepository.findById(bookingId).orElseThrow(
                () -> new HttpNotFoundException("Booking not found")
        );

        if (!Objects.equals(booking.getUserId(), userId)) {
            throw new HttpForbiddenError("You are not authorized to cancel this request");
        }

        if (booking.getBookingStatus() != BookingStatus.SCHEDULED
                && booking.getBookingStatus() != BookingStatus.AWAITING) {
            throw new HttpConflictException("Booking is not Scheduled");
        }

        booking.setBookingStatus(BookingStatus.CANCELLED_BY_USER);
        bookingRepository.save(booking);
    }

    public List<BookingDto> getAwaitingBookings(Long businessId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Business not found")
        );

        if (!Objects.equals(business.getUserId(), userId)) {
            throw new HttpForbiddenError("You are not authorized to view this business");
        }

        List<Service> services = business.getServices();

        return services.stream()
                .map(Service::getId)
                .map(bookingRepository::findAllByServiceId)
                .flatMap(List::stream)
                .filter(b -> b.getBookingStatus() == BookingStatus.AWAITING)
                .map(this::mapToDto)
                .toList();
    }

    public List<BookingDto> getScheduledBookings(Long businessId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Business not found")
        );

        if (!Objects.equals(business.getUserId(), userId)) {
            throw new HttpForbiddenError("You are not authorized to view this business");
        }

        List<Service> services = business.getServices();

        return services.stream()
                .map(Service::getId)
                .map(bookingRepository::findAllByServiceId)
                .flatMap(List::stream)
                .filter(b -> b.getBookingStatus() == BookingStatus.SCHEDULED)
                .map(this::mapToDto)
                .toList();
    }



    // mapToDto
    private BookingDto mapToDto(Booking b) {
        return new BookingDto(
                b.getId().toString(),
                b.getService().getName(),
                userService.getUserNameById(b.getUserId()),
                b.getStartTime(),
                b.getDuration(),
                b.getBookingStatus(),
                b.getBookingDate()
        );
    }
}
