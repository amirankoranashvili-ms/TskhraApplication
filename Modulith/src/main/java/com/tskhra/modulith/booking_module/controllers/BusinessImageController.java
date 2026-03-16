package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.responses.IdResponseDto;
import com.tskhra.modulith.booking_module.services.BusinessService;
import io.swagger.v3.oas.annotations.Operation;
import com.tskhra.modulith.booking_module.services.BusinessImageService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/business")
@RequiredArgsConstructor
public class BusinessImageController {

    private final BusinessImageService businessImageService;
    private final BusinessService businessService;

    @Operation(summary = "Upload a business image")
    @PostMapping(value = "/{id}/images", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<IdResponseDto> uploadBusinessImage(@AuthenticationPrincipal Jwt jwt,
                                                             @PathVariable("id") Long businessId,
                                                             @RequestParam(defaultValue = "false") boolean isMain,
                                                             @RequestParam("file") MultipartFile file) {

        Long id = businessImageService.uploadImage(file, jwt);
        businessService.addImageToBusiness(businessId, id, isMain);
        return ResponseEntity.status(HttpStatus.CREATED).body(new IdResponseDto(id.toString()));
    }

}
