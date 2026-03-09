package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.requests.BusinessDetailsDto;
import com.tskhra.modulith.booking_module.model.requests.BusinessRegistrationDto;
import com.tskhra.modulith.booking_module.model.responses.BusinessIdResponseDto;
import com.tskhra.modulith.booking_module.services.BusinessService;
import io.swagger.v3.oas.annotations.Hidden;
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

import java.util.List;

@RestController
@RequestMapping("/business")
@RequiredArgsConstructor
public class BusinessController {

    private final BusinessService businessService;

    @PostMapping("/individual")
    public ResponseEntity<BusinessIdResponseDto> createBusiness(@AuthenticationPrincipal Jwt jwt,
                                                                @Valid @RequestBody BusinessRegistrationDto dto) {

        Long id = businessService.register(dto, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(new BusinessIdResponseDto(id.toString()));
    }

    @GetMapping("/me")
    public ResponseEntity<List<BusinessDetailsDto>> getCurrentUserBusiness(@AuthenticationPrincipal Jwt jwt) {
        List<BusinessDetailsDto> businesses = businessService.getCurrentUserBusinesses(jwt);
        return ResponseEntity.ok(businesses);
    }

    @GetMapping
    public ResponseEntity<Page<BusinessDetailsDto>> getAllBusinesses(@RequestParam(defaultValue = "0") int page,
                                                                     @RequestParam(defaultValue = "12") int size) {

        Pageable pageable = PageRequest.of(page, size);
        Page<BusinessDetailsDto> businessPage = businessService.getAllBusinessPage(pageable);
        return ResponseEntity.ok(businessPage);
    }

    @GetMapping("/{id}")
    public ResponseEntity<BusinessDetailsDto> getBusiness(@PathVariable("id") Long businessId) {

        BusinessDetailsDto dto = businessService.getSpecificBusiness(businessId);
        return ResponseEntity.ok(dto);
    }

    @Hidden
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteBusiness(@PathVariable("id") Long businessId) {
        businessService.deleteBusiness(businessId);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }




}
