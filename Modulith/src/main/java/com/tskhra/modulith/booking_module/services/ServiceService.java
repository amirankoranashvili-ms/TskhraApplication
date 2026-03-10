package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.Booking;
import com.tskhra.modulith.booking_module.model.domain.Business;
import com.tskhra.modulith.booking_module.model.embeddable.ModificationDetails;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import com.tskhra.modulith.booking_module.model.enums.BookingStatus;
import com.tskhra.modulith.booking_module.model.requests.ServiceFullDto;
import com.tskhra.modulith.booking_module.model.requests.ServiceRegistrationDto;
import com.tskhra.modulith.booking_module.repositories.BookingRepository;
import com.tskhra.modulith.booking_module.repositories.BusinessRepository;
import com.tskhra.modulith.booking_module.repositories.ServiceRepository;
import com.tskhra.modulith.common.exception.HttpConflictException;
import com.tskhra.modulith.common.exception.HttpForbiddenError;
import com.tskhra.modulith.common.exception.HttpNotFoundException;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.transaction.annotation.Transactional;
import com.tskhra.modulith.booking_module.model.domain.Service;

import java.util.List;
import java.util.Objects;

@org.springframework.stereotype.Service
@RequiredArgsConstructor
public class ServiceService {

    private final ServiceRepository serviceRepository;
    private final BusinessRepository businessRepository;
    private final BookingRepository bookingRepository;
    private final UserService userService;
    
    private static final String BUSINESS_NOT_FOUND_MESSAGE = "Business not found with id: ";
    private static final String SERVICE_NOT_FOUND_MESSAGE = "Service not found with id: ";

    @Transactional
    public Long createService(ServiceRegistrationDto dto, Long businessId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(BUSINESS_NOT_FOUND_MESSAGE + businessId)
        );

        verifyOwnership(business, userId);

        Service service = Service.builder()
                .business(business)
                .activityStatus(ActivityStatus.ACTIVE)
                .name(dto.name())
                .description(dto.description())
                .capacity(1)
                .sessionPrice(dto.price())
                .sessionDuration(dto.duration())
                .modificationDetails(new ModificationDetails(userId, userId, null, null))
                .build();

        Service savedService = serviceRepository.save(service);
        return savedService.getId();
    }

    public List<ServiceFullDto> getBusinessServices(Long businessId) {
        businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(BUSINESS_NOT_FOUND_MESSAGE + businessId)
        );

        return serviceRepository.findByBusinessId(businessId).stream()
                .filter(s -> s.getActivityStatus() != ActivityStatus.DELETED)
                .map(this::mapToDto)
                .toList();
    }

    public ServiceFullDto getService(Long businessId, Long serviceId) {
        businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(BUSINESS_NOT_FOUND_MESSAGE + businessId)
        );

        Service service = serviceRepository.findByIdAndActivityStatus(serviceId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId)
        );

        if (!Objects.equals(service.getBusiness().getId(), businessId)) {
            throw new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId + " for business: " + businessId);
        }

        return mapToDto(service);
    }

    @Transactional
    public ServiceFullDto updateService(Long businessId, Long serviceId, ServiceRegistrationDto dto, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(BUSINESS_NOT_FOUND_MESSAGE + businessId)
        );

        verifyOwnership(business, userId);

        Service service = serviceRepository.findByIdAndActivityStatus(serviceId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId)
        );

        if (!Objects.equals(service.getBusiness().getId(), businessId)) {
            throw new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId + " for business: " + businessId);
        }

        service.setName(dto.name());
        service.setDescription(dto.description());
        service.setSessionPrice(dto.price());
        service.setSessionDuration(dto.duration());
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

        Service service = serviceRepository.findByIdAndActivityStatus(serviceId, ActivityStatus.ACTIVE).orElseThrow(
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

    private void verifyOwnership(Business business, Long userId) {
        if (!Objects.equals(business.getUserId(), userId)) {
            throw new HttpForbiddenError("You are not authorized to manage services for this business");
        }
    }

    public void changeServiceStatus(Long businessId, Long serviceId, ActivityStatus status, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(BUSINESS_NOT_FOUND_MESSAGE + businessId)
        );

        verifyOwnership(business, userId);

        if (status == ActivityStatus.DELETED) {
            throw new HttpConflictException("Cannot delete from here.");
        }

        Service service = serviceRepository.findByIdAndActivityStatus(serviceId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException(SERVICE_NOT_FOUND_MESSAGE + serviceId)
        );

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
