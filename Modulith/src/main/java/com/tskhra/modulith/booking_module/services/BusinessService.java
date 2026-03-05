package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.*;
import com.tskhra.modulith.booking_module.model.embeddable.ModificationDetails;
import com.tskhra.modulith.booking_module.model.enums.ActivityStatus;
import com.tskhra.modulith.booking_module.model.enums.BusinessType;
import com.tskhra.modulith.booking_module.model.requests.BusinessRegistrationDto;
import com.tskhra.modulith.booking_module.repositories.*;
import com.tskhra.modulith.common.exception.HttpNotFoundException;
import com.tskhra.modulith.user_module.services.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class BusinessService {

    private final BusinessRepository businessRepository;
    private final CityRepository cityRepository;
    private final AddressRepository addressRepository;
    private final CategoryRepository categoryRepository;
    private final BusinessImageRepository businessImageRepository;
    private final BusinessScheduleRepository businessScheduleRepository;
    private final BusinessUnavailableScheduleRepository businessUnavailableScheduleRepository;

    private final UserService userService;


    public Long register(@Valid BusinessRegistrationDto dto, Jwt jwt) {
        LocalDateTime now = LocalDateTime.now();
        Long userId = userService.getCurrentUser(jwt).getId();


//        Address
        String cityName = dto.city();
        City city = cityRepository.findByName(cityName)
                .orElseThrow(() -> new HttpNotFoundException("No such city: " + cityName));
        Address address = new Address();
        address.setCity(city);
        address.setDetails(dto.addressDetails());
        Address savedAddress = addressRepository.save(address);

//        Business
        Business business = Business.builder()
                .name(dto.businessName())
                .userId(userId)
                .description(dto.description())
                .phoneNumber(dto.info().phoneNumber())
                .instagramUrl(dto.info().instagramUrl())
                .facebookUrl(dto.info().facebookUrl())
                .businessType(BusinessType.INDIVIDUAL)
                .activityStatus(ActivityStatus.ACTIVE)
                .callType(dto.callType())
                .modificationDetails(new ModificationDetails(userId, userId, now, now))
                .build();

        Business savedBusiness = businessRepository.save(business);
        savedBusiness.setAddress(savedAddress);

//        Category
        String categoryName = dto.subCategory();
        Category category = categoryRepository.findByName(categoryName)
                .orElseThrow(() -> new HttpNotFoundException("No such category: " + categoryName));
        savedBusiness.setCategory(category);

//        Main Image
        Long mainImageId = Long.valueOf(dto.mainImageId());
        BusinessImage mainImage = businessImageRepository.findById(mainImageId)
                .orElseThrow(() -> new HttpNotFoundException("No such image with id " + mainImageId));
        mainImage.setBusiness(savedBusiness);
        mainImage.setMain(true);

//        Gallery Images
        dto.galleryImageIds().stream()
                .map(Long::valueOf)
                .map(businessImageRepository::findById)
                .map(opt ->
                        opt.orElseThrow(() -> new HttpNotFoundException("No such image with id " + mainImageId)))
                .forEach(businessImage -> businessImage.setBusiness(savedBusiness));

//        Work Times
        dto.workTimes().stream()
                .map(interval -> new BusinessSchedule(null, savedBusiness, interval))
                .forEach(businessScheduleRepository::save);

//        Rest Times
        dto.restTimes().stream()
                .map(interval -> new BusinessUnavailableSchedule(null, savedBusiness, interval))
                .forEach(businessUnavailableScheduleRepository::save);

        return savedBusiness.getId();
    }
}
