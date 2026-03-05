package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.requests.BusinessRegistrationDto;
import com.tskhra.modulith.booking_module.model.responses.IdResponseDto;
import com.tskhra.modulith.booking_module.services.BusinessService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/business")
@RequiredArgsConstructor
public class BusinessController {

    private final BusinessService businessService;

    @PostMapping("/individual")
    public ResponseEntity<IdResponseDto> createBusiness(@AuthenticationPrincipal Jwt jwt,
                                                        @Valid @RequestBody BusinessRegistrationDto dto) {

        Long id = businessService.register(dto, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(new IdResponseDto(id.toString()));
    }

}
