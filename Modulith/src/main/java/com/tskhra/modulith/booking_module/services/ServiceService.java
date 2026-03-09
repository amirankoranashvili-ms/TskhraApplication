package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.Business;
import com.tskhra.modulith.booking_module.model.embeddable.ModificationDetails;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import com.tskhra.modulith.booking_module.model.requests.ServiceFullDto;
import com.tskhra.modulith.booking_module.model.requests.ServiceRegistrationDto;
import com.tskhra.modulith.booking_module.repositories.BusinessRepository;
import com.tskhra.modulith.booking_module.repositories.ServiceRepository;
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
    private final UserService userService;

    @Transactional
    public Long createService(ServiceRegistrationDto dto, Long businessId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Business not found with id: " + businessId)
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

    @Transactional(readOnly = true)
    public List<ServiceFullDto> getBusinessServices(Long businessId) {
        businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Business not found with id: " + businessId)
        );

        return serviceRepository.findByBusinessIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).stream()
                .map(this::mapToDto)
                .toList();
    }

    @Transactional(readOnly = true)
    public ServiceFullDto getService(Long businessId, Long serviceId) {
        businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Business not found with id: " + businessId)
        );

        Service service = serviceRepository.findByIdAndActivityStatus(serviceId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Service not found with id: " + serviceId)
        );

        if (!Objects.equals(service.getBusiness().getId(), businessId)) {
            throw new HttpNotFoundException("Service not found with id: " + serviceId + " for business: " + businessId);
        }

        return mapToDto(service);
    }

    @Transactional
    public ServiceFullDto updateService(Long businessId, Long serviceId, ServiceRegistrationDto dto, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Business not found with id: " + businessId)
        );

        verifyOwnership(business, userId);

        Service service = serviceRepository.findByIdAndActivityStatus(serviceId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Service not found with id: " + serviceId)
        );

        if (!Objects.equals(service.getBusiness().getId(), businessId)) {
            throw new HttpNotFoundException("Service not found with id: " + serviceId + " for business: " + businessId);
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
                () -> new HttpNotFoundException("Business not found with id: " + businessId)
        );

        verifyOwnership(business, userId);

        Service service = serviceRepository.findByIdAndActivityStatus(serviceId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Service not found with id: " + serviceId)
        );

        if (!Objects.equals(service.getBusiness().getId(), businessId)) {
            throw new HttpNotFoundException("Service not found with id: " + serviceId + " for business: " + businessId);
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
                s.getSessionDuration()
        );
    }

    private void verifyOwnership(Business business, Long userId) {
        if (!Objects.equals(business.getUserId(), userId)) {
            throw new HttpForbiddenError("You are not authorized to manage services for this business");
        }
    }
}
