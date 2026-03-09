package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.responses.IdResponseDto;
import io.swagger.v3.oas.annotations.Operation;
import com.tskhra.modulith.booking_module.services.BusinessImageService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/business")
@RequiredArgsConstructor
public class BusinessImageController {

    private final BusinessImageService businessImageService;

    @Operation(summary = "Upload a business image")
    @PostMapping(value = "/images", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<IdResponseDto> uploadBusinessImage(@AuthenticationPrincipal Jwt jwt,
                                                             @RequestParam("file") MultipartFile file) {

        Long id = businessImageService.uploadImage(file, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(new IdResponseDto(id.toString()));
    }

}
