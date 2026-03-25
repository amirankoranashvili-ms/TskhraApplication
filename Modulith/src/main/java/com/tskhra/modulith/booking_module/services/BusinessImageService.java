package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.Business;
import com.tskhra.modulith.booking_module.model.domain.BusinessImage;
import com.tskhra.modulith.booking_module.repositories.BusinessImageRepository;
import com.tskhra.modulith.booking_module.repositories.BusinessRepository;
import com.tskhra.modulith.common.exception.http_exceptions.HttpForbiddenError;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.common.services.ImageService;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class BusinessImageService {

    private final BusinessImageRepository businessImageRepository;
    private final BusinessRepository businessRepository;
    private final ImageService imageService;
    private final UserService userService;


    public Long uploadImage(MultipartFile file, Long businessId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        verifyOwnership(businessId, userId);
        String filename = imageService.uploadBusinessImage(file);
        BusinessImage businessImage = BusinessImage.builder()
                .filename(filename)
                .uploadedBy(userId)
                .build();

        BusinessImage saved = businessImageRepository.save(businessImage);
        return saved.getId();
    }

    public void verifyOwnership(Long businessId, Long userId) {
        Business business = businessRepository.findById(businessId)
                .orElseThrow(() -> new HttpNotFoundException("Business not found"));
        if (!business.getUserId().equals(userId)) {
            throw new HttpForbiddenError("You are not authorized to perform this action");
        }
    }
}
