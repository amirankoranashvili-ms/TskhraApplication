package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.*;
import com.tskhra.modulith.booking_module.model.enums.*;
import com.tskhra.modulith.booking_module.model.events.*;
import com.tskhra.modulith.booking_module.model.requests.IndividualBookingRequest;
import com.tskhra.modulith.booking_module.model.responses.BookingDto;
import com.tskhra.modulith.booking_module.repositories.*;
import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpConflictException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpForbiddenError;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.transaction.annotation.Transactional;
import com.tskhra.modulith.booking_module.model.domain.Service;
import tools.jackson.databind.ObjectMapper;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

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
    private final ApplicationEventPublisher eventPublisher;
    private final SimpMessagingTemplate simpMessagingTemplate;
    private final ObjectMapper objectMapper;

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

        // Serialize concurrent bookings for this business+date via PostgreSQL advisory lock.
        // Blocks until any competing transaction for the same business+date commits/rolls back.
        bookingRepository.lockBusinessDate(business.getId(), request.date());

        int endTime = request.startTime() + service.getSessionDuration();
        if (!isTimeAvailable(business.getId(), request.date(), request.startTime(), endTime)) {
            throw new HttpConflictException("Time slot not available");
        }

        String userKeycloakId = jwt.getClaimAsString("sub");
        String businessOwnerId = userService.getUserKeycloakIdById(business.getUserId());
        String bookedBy = userService.getCurrentUser(jwt).getUsername();

        Resource res = getOrCreateIndividualResource(business);

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

//        eventPublisher.publishEvent(new BookingStatusChangedEvent(
//                booking.getId(), business.getUserId(), BookingStatus.AWAITING,
//                service.getName(), business.getName()
//        ));

        BookingEvent bookingEvent = new BookingEvent(business.getId(), bookedBy, service.getId(), booking.getBookingDate(), booking.getStartTime());
        simpMessagingTemplate.convertAndSend("/topic/bookings", "User " + userId + " has booked a service: " + service.getName() + " on " + request.date() + " at " + request.startTime());
        simpMessagingTemplate.convertAndSendToUser(businessOwnerId, "/queue/messages", objectMapper.writeValueAsString(bookingEvent));

//        eventPublisher.publishEvent(new BookingCreatedEvent(
//                UUID.randomUUID().toString(),
//                LocalDateTime.now(),
//                "booking_service",
//                booking.getId().toString(),
//                new BookingCreatedEvent.Payload(
//                        business.getId().toString(),
//                        service.getId().toString(),
//                        userKeycloakId,
//                        booking.getId().toString(),
//                        request.date().toString(),
//                        request.startTime()
//                )
//        ));
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

        boolean overlapsBooking = bookingRepository.existsOverlappingBooking(
                businessId, date, List.of(BookingStatus.AWAITING, BookingStatus.SCHEDULED), startTime, endTime
        );
        return !overlapsBooking;
    }

    private Resource getOrCreateIndividualResource(Business business) {
        List<Resource> activeResources = resourceRepository.findByBusinessIdAndActivityStatus(business.getId(), ActivityStatus.ACTIVE);
        if (activeResources.isEmpty()) {
            Resource resource = new Resource();
            resource.setBusiness(business);
            resource.setName("self");
            resource.setActivityStatus(ActivityStatus.ACTIVE);
            return resourceRepository.save(resource);
        }
        return activeResources.getFirst();
    }

    @Transactional
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

        if (booking.getBookingDate().isBefore(LocalDate.now())) {
            throw new HttpBadRequestException("Cannot approve a booking in the past");
        }

        booking.setBookingStatus(BookingStatus.SCHEDULED);
        bookingRepository.save(booking);

//        eventPublisher.publishEvent(new BookingStatusChangedEvent(
//                booking.getId(), booking.getUserId(), BookingStatus.SCHEDULED,
//                service.getName(), business.getName()
//        ));

        BookingStatusChangeEvent statusChangeEvent = new BookingStatusChangeEvent(
                service.getId(), business.getId(), BookingStatus.SCHEDULED, booking.getBookingDate(), booking.getStartTime()
        );
        String bookedBy = userService.getUserKeycloakIdById(booking.getUserId());
        simpMessagingTemplate.convertAndSendToUser(
                bookedBy, "/queue/statuschange", objectMapper.writeValueAsString(statusChangeEvent));

//        eventPublisher.publishEvent(new BookingApprovedEvent(
//                UUID.randomUUID().toString(),
//                LocalDateTime.now(),
//                "approve_booking_service_by_business",
//                booking.getId().toString(),
//                new BookingApprovedEvent.Payload(
//                        business.getId().toString(),
//                        booking.getId().toString()
//                )
//        ));
    }

    @Transactional
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

//        eventPublisher.publishEvent(new BookingStatusChangedEvent(
//                booking.getId(), booking.getUserId(), BookingStatus.REJECTED,
//                service.getName(), business.getName()
//        ));

        BookingStatusChangeEvent statusChangeEvent = new BookingStatusChangeEvent(
                service.getId(), business.getId(), BookingStatus.REJECTED, booking.getBookingDate(), booking.getStartTime()
        );
        String bookedBy = userService.getUserKeycloakIdById(booking.getUserId());
        simpMessagingTemplate.convertAndSendToUser(
                bookedBy, "/queue/statuschange", objectMapper.writeValueAsString(statusChangeEvent));

//        eventPublisher.publishEvent(new BookingRejectedEvent(
//                UUID.randomUUID().toString(),
//                LocalDateTime.now(),
//                "reject_booking_service_by_business",
//                booking.getId().toString(),
//                new BookingRejectedEvent.Payload(
//                        business.getId().toString(),
//                        booking.getId().toString()
//                )
//        ));
    }

    @Transactional
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

//        eventPublisher.publishEvent(new BookingStatusChangedEvent(
//                booking.getId(), booking.getUserId(), BookingStatus.CANCELLED_BY_BUSINESS,
//                service.getName(), business.getName()
//        ));

        BookingStatusChangeEvent statusChangeEvent = new BookingStatusChangeEvent(
                service.getId(), business.getId(), BookingStatus.CANCELLED_BY_BUSINESS, booking.getBookingDate(), booking.getStartTime()
        );
        String bookedBy = userService.getUserKeycloakIdById(booking.getUserId());
        simpMessagingTemplate.convertAndSendToUser(
                bookedBy, "/queue/statuschange", objectMapper.writeValueAsString(statusChangeEvent));

//        eventPublisher.publishEvent(new BookingCancelledByBusinessEvent(
//                UUID.randomUUID().toString(),
//                LocalDateTime.now(),
//                "cancel_booking_by_business_after_approve",
//                booking.getId().toString(),
//                new BookingCancelledByBusinessEvent.Payload(
//                        business.getId().toString(),
//                        booking.getId().toString()
//                )
//        ));
    }

    @Transactional
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

        String previousStatus = booking.getBookingStatus().name();
        booking.setBookingStatus(BookingStatus.CANCELLED_BY_USER);
        bookingRepository.save(booking);

        Service service = booking.getService();
        Business business = service.getBusiness();
//        eventPublisher.publishEvent(new BookingStatusChangedEvent(
//                booking.getId(), business.getUserId(), BookingStatus.CANCELLED_BY_USER,
//                service.getName(), business.getName()
//        ));

        BookingStatusChangeEvent statusChangeEvent = new BookingStatusChangeEvent(
                service.getId(), business.getId(), BookingStatus.CANCELLED_BY_USER, booking.getBookingDate(), booking.getStartTime()
        );
        String businessOwner = userService.getUserKeycloakIdById(business.getUserId());
        simpMessagingTemplate.convertAndSendToUser(
                businessOwner, "/queue/statuschange", objectMapper.writeValueAsString(statusChangeEvent));

        String userKeycloakId = jwt.getClaimAsString("sub");
//        eventPublisher.publishEvent(new BookingCancelledByUserEvent(
//                UUID.randomUUID().toString(),
//                LocalDateTime.now(),
//                "cancel_booking_by_user",
//                booking.getId().toString(),
//                new BookingCancelledByUserEvent.Payload(
//                        userKeycloakId,
//                        booking.getId().toString(),
//                        previousStatus
//                )
//        ));
    }

    public List<BookingDto> getAwaitingBookings(Long businessId, Lang lang, Jwt jwt) {

        List<Service> services = getBusinessServices(businessId, jwt);

        return services.stream()
                .map(Service::getId)
                .map(bookingRepository::findAllByServiceId)
                .flatMap(List::stream)
                .filter(b -> b.getBookingStatus() == BookingStatus.AWAITING)
//                .filter(b -> !b.getBookingDate().isBefore(LocalDate.now()))
                .map(b -> mapToDto(b, lang))
                .toList();
    }

    private List<Service> getBusinessServices(Long businessId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Business not found")
        );

        if (!Objects.equals(business.getUserId(), userId)) {
            throw new HttpForbiddenError("You are not authorized to view this business");
        }

        return business.getServices();
    }

    public List<BookingDto> getScheduledBookings(Long businessId, Lang lang, Jwt jwt) {
        List<Service> services = getBusinessServices(businessId, jwt);

        return services.stream()
                .map(Service::getId)
                .map(bookingRepository::findAllByServiceId)
                .flatMap(List::stream)
                .filter(b -> b.getBookingStatus() == BookingStatus.SCHEDULED)
//                .filter(b -> !b.getBookingDate().isBefore(LocalDate.now()))
                .map(b -> mapToDto(b, lang))
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
                b.getBookingDate(),
                b.getService().getSessionPrice()
        );
    }

    private BookingDto mapToDto(Booking b, Lang lang) {
        String serviceName = switch (lang) {
            case KA -> b.getService().getNameKa() == null ? b.getService().getName() : b.getService().getNameKa();
            case EN -> b.getService().getName();
        };
        return new BookingDto(
                b.getId().toString(),
                serviceName,
                userService.getUserNameById(b.getUserId()),
                b.getStartTime(),
                b.getDuration(),
                b.getBookingStatus(),
                b.getBookingDate(),
                b.getService().getSessionPrice()
        );
    }

    public Page<BookingDto> getCurrentUserBookings(Jwt jwt, Lang lang, Pageable pageable) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Page<Booking> page = bookingRepository.findAllActiveByUserId(userId, pageable, List.of(BookingStatus.AWAITING, BookingStatus.SCHEDULED));
        return page.map(b -> mapToDto(b, lang));
    }
}
