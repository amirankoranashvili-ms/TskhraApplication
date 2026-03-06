package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.Business;
import com.tskhra.modulith.booking_module.model.embeddable.ModificationDetails;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import com.tskhra.modulith.booking_module.model.requests.ServiceRegistrationDto;
import com.tskhra.modulith.booking_module.repositories.BusinessRepository;
import com.tskhra.modulith.booking_module.repositories.ServiceRepository;
import com.tskhra.modulith.common.exception.HttpNotFoundException;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import com.tskhra.modulith.booking_module.model.domain.Service;

import java.util.List;

@org.springframework.stereotype.Service
@RequiredArgsConstructor
public class ServiceService {

    private final ServiceRepository serviceRepository;
    private final BusinessRepository businessRepository;
    private final UserService userService;

    public Long createService(ServiceRegistrationDto dto, Long businessId, Jwt jwt) {
        Business business = businessRepository.findById(businessId).orElseThrow(
                () -> new HttpNotFoundException("Business not found with id: " + businessId)
        );

        Long userId = userService.getCurrentUser(jwt).getId();
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

}
