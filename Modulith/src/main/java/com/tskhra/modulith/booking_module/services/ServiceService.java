package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.Booking;
import com.tskhra.modulith.booking_module.model.domain.Business;
import com.tskhra.modulith.booking_module.model.embeddable.ModificationDetails;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import com.tskhra.modulith.booking_module.model.enums.BookingStatus;
import com.tskhra.modulith.booking_module.model.enums.Lang;
import com.tskhra.modulith.booking_module.model.events.ServiceCreatedEvent;
import com.tskhra.modulith.booking_module.model.events.ServiceDeactivatedEvent;
import com.tskhra.modulith.booking_module.model.requests.ServiceFullDto;
import com.tskhra.modulith.booking_module.model.requests.ServiceRegistrationDto;
import com.tskhra.modulith.booking_module.model.requests.ServiceUpdateDto;
import com.tskhra.modulith.booking_module.repositories.BookingRepository;
import com.tskhra.modulith.booking_module.repositories.BusinessRepository;
import com.tskhra.modulith.booking_module.repositories.ServiceRepository;
import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpConflictException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpForbiddenError;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.transaction.annotation.Transactional;
import com.tskhra.modulith.booking_module.model.domain.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

@org.springframework.stereotype.Service
@RequiredArgsConstructor
public class ServiceService {

    private final ServiceRepository serviceRepository;
    private final BusinessRepository businessRepository;
    private final BookingRepository bookingRepository;
    private final UserService userService;
    private final ApplicationEventPublisher eventPublisher;

    private static final String BUSINESS_NOT_FOUND_MESSAGE = "Business not found with id: ";
    private static final String SERVICE_NOT_FOUND_MESSAGE = "Service not found with id: ";

    @Transactional
    public Long createService(ServiceRegistrationDto dto, Long businessId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(BUSINESS_NOT_FOUND_MESSAGE + businessId)
        );

        verifyOwnership(business, userId);

        if (dto.description() == null ^ dto.descriptionKa() == null) {
            throw new HttpBadRequestException("Both description and description_ka must be provided or not provided");
        }

        if (dto.description().isBlank() ^ dto.descriptionKa().isBlank()) {
            throw new HttpBadRequestException("Both description and description_ka must be provided or not provided");
        }

        Service service = Service.builder()
                .business(business)
                .activityStatus(ActivityStatus.ACTIVE)
                .name(dto.name())
                .nameKa(dto.nameKa())
                .description(dto.description())
                .descriptionKa(dto.descriptionKa())
                .capacity(1)
                .sessionPrice(dto.price())
                .sessionDuration(dto.duration())
                .modificationDetails(new ModificationDetails(userId, userId, null, null))
                .build();

        Service savedService = serviceRepository.save(service);

        eventPublisher.publishEvent(new ServiceCreatedEvent(
                UUID.randomUUID().toString(),
                LocalDateTime.now(),
                "create_new_service",
                savedService.getId().toString(),
                new ServiceCreatedEvent.Payload(
                        businessId.toString(),
                        savedService.getId().toString(),
                        dto.name(),
                        dto.nameKa(),
                        dto.description(),
                        dto.descriptionKa(),
                        dto.price(),
                        dto.duration()
                )
        ));

        return savedService.getId();
    }

    public List<ServiceFullDto> getBusinessServices(Long businessId, Lang lang) {
        businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(BUSINESS_NOT_FOUND_MESSAGE + businessId)
        );

        return serviceRepository.findByBusinessId(businessId).stream()
                .filter(s -> s.getActivityStatus() != ActivityStatus.DELETED)
                .map(s -> mapToDto(s, lang))
                .toList();
    }

    public ServiceFullDto getService(Long businessId, Long serviceId, Lang lang) {
        businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(BUSINESS_NOT_FOUND_MESSAGE + businessId)
        );

        Service service = serviceRepository.findByIdAndActivityStatus(serviceId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId)
        );

        if (!Objects.equals(service.getBusiness().getId(), businessId)) {
            throw new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId + " for business: " + businessId);
        }

        return mapToDto(service, lang);
    }

    @Transactional
    public ServiceFullDto updateService(Long businessId, Long serviceId, ServiceUpdateDto dto, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(BUSINESS_NOT_FOUND_MESSAGE + businessId)
        );

        verifyOwnership(business, userId);

        Service service = serviceRepository.findById(serviceId).orElseThrow(
                () -> new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId)
        );

        if (service.getActivityStatus() == ActivityStatus.DELETED) {
            throw new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId);
        }


        if (!Objects.equals(service.getBusiness().getId(), businessId)) {
            throw new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId + " for business: " + businessId);
        }

        String name = dto.name();
        String nameKa = dto.nameKa();
        String description = dto.description();
        String descriptionKa = dto.descriptionKa();

        if (name != null) {
            service.setName(dto.name());
        }
        if (nameKa != null) {
            service.setNameKa(dto.nameKa());
        }
        if (description != null) {
            service.setDescription(dto.description());
        }
        if (descriptionKa != null) {
            service.setDescriptionKa(dto.descriptionKa());
        }


        service.getModificationDetails().setUpdatedBy(userId);

        Service saved = serviceRepository.save(service);
        return mapToDto(saved);
    }

    @Transactional
    public void deleteService(Long businessId, Long serviceId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(BUSINESS_NOT_FOUND_MESSAGE + businessId)
        );

        verifyOwnership(business, userId);

        Service service = serviceRepository.findById(serviceId).orElseThrow(
                () -> new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId)
        );

        if (!Objects.equals(service.getBusiness().getId(), businessId)) {
            throw new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId + " for business: " + businessId);
        }

        if (service.getActivityStatus() != ActivityStatus.INACTIVE) {
            throw new HttpConflictException("Cannot delete. Service is not INACTIVE.");
        }

        service.setActivityStatus(ActivityStatus.DELETED);
        serviceRepository.save(service);
    }

    private ServiceFullDto mapToDto(Service s) {
        return new ServiceFullDto(
                s.getId().toString(),
                s.getName(),
                s.getDescription(),
                s.getSessionPrice(),
                s.getSessionDuration(),
                s.getActivityStatus()
        );
    }

    private ServiceFullDto mapToDto(Service s, Lang lang) {
        String name = switch (lang) {
            case KA -> s.getNameKa() == null || s.getNameKa().isBlank() ? s.getName() : s.getNameKa();
            case EN -> s.getName() == null || s.getName().isBlank() ? s.getNameKa() : s.getName();
        };
        String description = switch (lang) {
            case KA ->
                    s.getDescriptionKa() == null || s.getDescriptionKa().isBlank() ? s.getDescription() : s.getDescriptionKa();
            case EN ->
                    s.getDescription() == null || s.getDescription().isBlank() ? s.getDescriptionKa() : s.getDescription();
        };
        return new ServiceFullDto(
                s.getId().toString(),
                name,
                description,
                s.getSessionPrice(),
                s.getSessionDuration(),
                s.getActivityStatus()
        );
    }

    private void verifyOwnership(Business business, Long userId) {
        if (!Objects.equals(business.getUserId(), userId)) {
            throw new HttpForbiddenError("You are not authorized to manage services for this business");
        }
    }

    @Transactional
    public void changeServiceStatus(Long businessId, Long serviceId, ActivityStatus status, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(BUSINESS_NOT_FOUND_MESSAGE + businessId)
        );

        verifyOwnership(business, userId);

        if (status == ActivityStatus.DELETED) {
            throw new HttpConflictException("Cannot delete from here.");
        }

        Service service = serviceRepository.findById(serviceId).orElseThrow(
                () -> new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId)
        );

        if (service.getActivityStatus() == ActivityStatus.DELETED) {
            throw new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId);
        }

        if (status == ActivityStatus.ACTIVE) {
            if (service.getActivityStatus() != ActivityStatus.INACTIVE) {
                throw new HttpConflictException("Service must be inactive to activate it.");
            }

            service.setActivityStatus(ActivityStatus.ACTIVE);
            serviceRepository.save(service);
            return;
        }

        if (status == ActivityStatus.INACTIVE) {
            if (service.getActivityStatus() != ActivityStatus.ACTIVE) {
                throw new HttpConflictException("Service must be active to deactivate it.");
            }

            cancelServiceBookings(serviceId);

            service.setActivityStatus(ActivityStatus.INACTIVE);
            serviceRepository.save(service);

            eventPublisher.publishEvent(new ServiceDeactivatedEvent(
                    UUID.randomUUID().toString(),
                    LocalDateTime.now(),
                    "deactivate_service",
                    serviceId.toString(),
                    new ServiceDeactivatedEvent.Payload(
                            businessId.toString(),
                            serviceId.toString()
                    )
            ));
        }
    }

    private void cancelServiceBookings(Long serviceId) {
        List<Booking> awaitingBookings =
                bookingRepository.findAllByService_IdAndBookingStatus(serviceId, BookingStatus.AWAITING);

        List<Booking> scheduledBookings =
                bookingRepository.findAllByService_IdAndBookingStatus(serviceId, BookingStatus.SCHEDULED);

        awaitingBookings.forEach(b -> b.setBookingStatus(BookingStatus.REJECTED));
        scheduledBookings.forEach(b -> b.setBookingStatus(BookingStatus.CANCELLED_BY_BUSINESS));
    }
}
