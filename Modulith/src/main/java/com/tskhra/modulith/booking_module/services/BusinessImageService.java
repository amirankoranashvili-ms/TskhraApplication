package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.BusinessImage;
import com.tskhra.modulith.booking_module.repositories.BusinessImageRepository;
import com.tskhra.modulith.common.services.ImageService;
import com.tskhra.modulith.user_module.model.domain.User;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class BusinessImageService {

    private final BusinessImageRepository businessImageRepository;
    private final ImageService imageService;
    private final UserService userService;


    public Long uploadImage(MultipartFile file, Jwt jwt) { // todo check createdAt
        Long userId = userService.getCurrentUser(jwt).getId();
        String filename = imageService.uploadBusinessImage(file);
        BusinessImage businessImage = BusinessImage.builder()
                .filename(filename)
                .uploadedBy(userId)
                .build();

        BusinessImage saved = businessImageRepository.save(businessImage);
        return saved.getId();
    }
}
