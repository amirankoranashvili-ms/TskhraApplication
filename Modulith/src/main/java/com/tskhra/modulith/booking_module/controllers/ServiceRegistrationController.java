package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.requests.ServiceFullDto;
import com.tskhra.modulith.booking_module.model.requests.ServiceRegistrationDto;
import com.tskhra.modulith.booking_module.model.responses.IdResponseDto;
import com.tskhra.modulith.booking_module.services.ServiceService;
import io.swagger.v3.oas.annotations.Operation;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/business")
@RequiredArgsConstructor
@Slf4j
public class ServiceRegistrationController {

    private final ServiceService serviceService;

    @Operation(summary = "Add a service to a business")
    @PostMapping("/{id}/services")
    public ResponseEntity<IdResponseDto> createService(@AuthenticationPrincipal Jwt jwt,
                                                             @PathVariable("id") Long businessId,
                                                             @Valid @RequestBody ServiceRegistrationDto dto) {

        Long createdId = serviceService.createService(dto, businessId, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(new IdResponseDto(createdId.toString()));
    }

    @Operation(summary = "List services of a business")
    @GetMapping("/{id}/services")
    public ResponseEntity<List<ServiceFullDto>> getBusinessServices(@PathVariable("id") Long businessId) {

        List<ServiceFullDto> services = serviceService.getBusinessServices(businessId);
        return ResponseEntity.ok(services);
    }

    @Operation(summary = "Get a specific business service")
    @GetMapping("/{businessId}/services/{serviceId}")
    public ResponseEntity<ServiceFullDto> getService(@PathVariable Long businessId,
                                                     @PathVariable Long serviceId) {
        ServiceFullDto service = serviceService.getService(businessId, serviceId);
        return ResponseEntity.ok(service);
    }

    @Operation(summary = "Update a business service")
    @PutMapping("/{businessId}/services/{serviceId}")
    public ResponseEntity<ServiceFullDto> updateService(@AuthenticationPrincipal Jwt jwt,
                                                        @PathVariable Long businessId,
                                                        @PathVariable Long serviceId,
                                                        @Valid @RequestBody ServiceRegistrationDto dto) {
        ServiceFullDto updated = serviceService.updateService(businessId, serviceId, dto, jwt);
        return ResponseEntity.ok(updated);
    }

    @Operation(summary = "Delete a business service")
    @DeleteMapping("/{businessId}/services/{serviceId}")
    public ResponseEntity<Void> deleteService(@AuthenticationPrincipal Jwt jwt,
                                              @PathVariable Long businessId,
                                              @PathVariable Long serviceId) {
        serviceService.deleteService(businessId, serviceId, jwt);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
