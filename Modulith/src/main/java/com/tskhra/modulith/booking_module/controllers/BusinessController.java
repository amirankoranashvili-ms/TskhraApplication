package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.enums.Lang;
import com.tskhra.modulith.booking_module.model.requests.BusinessDetailsDto;
import com.tskhra.modulith.booking_module.model.requests.BusinessRegistrationDto;
import com.tskhra.modulith.booking_module.model.requests.BusinessUpdateDto;
import com.tskhra.modulith.booking_module.model.requests.TimeslotRequest;
import com.tskhra.modulith.booking_module.model.responses.BusinessIdResponseDto;
import com.tskhra.modulith.booking_module.services.BusinessService;
import io.swagger.v3.oas.annotations.Operation;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/business")
@RequiredArgsConstructor
public class BusinessController {

    private final BusinessService businessService;

    @Operation(summary = "Register a new individual business")
    @PostMapping("/individual")
    public ResponseEntity<BusinessIdResponseDto> createBusiness(@AuthenticationPrincipal Jwt jwt,
                                                                @Valid @RequestBody BusinessRegistrationDto dto) {

        Long id = businessService.register(dto, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(new BusinessIdResponseDto(id.toString()));
    }

    @Operation(summary = "Get current user's businesses")
    @GetMapping("/me")
    public ResponseEntity<List<BusinessDetailsDto>> getCurrentUserBusiness(@AuthenticationPrincipal Jwt jwt,
                                                                           @RequestParam(defaultValue = "EN") Lang lang) {
        List<BusinessDetailsDto> businesses = businessService.getCurrentUserBusinesses(lang, jwt);
        return ResponseEntity.ok(businesses);
    }

    @Operation(summary = "List all businesses (paginated). NOTE: filtering by category currently works ONLY with SUBCATEGORIES.: ")
    @GetMapping
    public ResponseEntity<Page<BusinessDetailsDto>> getAllBusinesses(@RequestParam(defaultValue = "0") int page,
                                                                     @RequestParam(defaultValue = "12") int size,
                                                                     @RequestParam(defaultValue = "EN") Lang lang,
                                                                     @RequestParam(required = false) Long categoryId) {

        Pageable pageable = PageRequest.of(page, size);
        Page<BusinessDetailsDto> businessPage = businessService.getAllBusinessPage(lang, categoryId, pageable);
        return ResponseEntity.ok(businessPage);
    }

    @Operation(summary = "Get business by ID")
    @GetMapping("/{id}")
    public ResponseEntity<BusinessDetailsDto> getBusiness(@PathVariable("id") Long businessId,
                                                          @RequestParam(defaultValue = "EN") Lang lang) {

        BusinessDetailsDto dto = businessService.getSpecificBusiness(businessId, lang);
        return ResponseEntity.ok(dto);
    }

    @Operation(summary = "Update business by ID")
    @PutMapping("/{id}")
    public ResponseEntity<BusinessDetailsDto> updateBusiness(@AuthenticationPrincipal Jwt jwt,
                                                             @PathVariable("id") Long businessId,
                                                             @Valid @RequestBody BusinessUpdateDto dto) {
        BusinessDetailsDto updated = businessService.updateBusiness(businessId, dto, jwt);
        return ResponseEntity.ok(updated);
    }

    @Operation(summary = "Delete business by ID")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteBusiness(@PathVariable("id") Long businessId, @AuthenticationPrincipal Jwt jwt) {
        businessService.deleteBusiness(businessId, jwt);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

    @GetMapping("/{id}/timeslots")
    public ResponseEntity<List<Integer>> getBusinessAvailableTimeslots(@PathVariable("id") Long businessId,
                                                                       @RequestParam("date") LocalDate date,
                                                                       @RequestParam("serviceId") String serviceId,
                                                                       @RequestParam(defaultValue = "10") int slotInterval) {

        List<Integer> validStartTimes = businessService.getAvailableStartTimes(businessId, new TimeslotRequest(date, serviceId, slotInterval));
        return ResponseEntity.ok(validStartTimes);
    }


}
