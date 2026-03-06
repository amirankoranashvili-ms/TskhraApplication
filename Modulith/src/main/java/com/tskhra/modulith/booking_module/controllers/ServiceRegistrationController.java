package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.requests.ServiceRegistrationDto;
import com.tskhra.modulith.booking_module.model.responses.IdResponseDto;
import com.tskhra.modulith.booking_module.services.BusinessService;
import com.tskhra.modulith.booking_module.services.ServiceService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/business")
@RequiredArgsConstructor
@Slf4j
public class ServiceRegistrationController {

    private final ServiceService serviceService;

    @PostMapping("/{id}/services")
    public ResponseEntity<List<IdResponseDto>> createService(@AuthenticationPrincipal Jwt jwt,
                                                       @PathVariable("id") Long businessId,
                                                       @RequestBody List<ServiceRegistrationDto> dtos) {

        log.warn("Creating service for business: {}", businessId);
        log.warn("Service: {}", dtos);
        List<Long> createdId = serviceService.createServices(dtos, businessId, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(
                createdId.stream()
                        .map(Object::toString)
                        .map(IdResponseDto::new)
                        .toList()
        );
    }

    @PostMapping("/{id}/services/single")
    public ResponseEntity<IdResponseDto> createService(@AuthenticationPrincipal Jwt jwt,
                                                       @PathVariable("id") Long businessId,
                                                       @RequestBody ServiceRegistrationDto dto) {

        log.warn("Creating service for business: {}", businessId);
        log.warn("Service: {}", dto);
        Long createdId = serviceService.createService(dto, businessId, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(new IdResponseDto(createdId.toString()));
    }

}
