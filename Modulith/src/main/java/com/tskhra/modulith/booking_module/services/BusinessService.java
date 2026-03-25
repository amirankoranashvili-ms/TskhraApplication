package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.*;
import com.tskhra.modulith.booking_module.model.embeddable.ModificationDetails;
import com.tskhra.modulith.booking_module.model.embeddable.WeekTimeInterval;
import com.tskhra.modulith.booking_module.model.enums.*;
import com.tskhra.modulith.booking_module.model.requests.*;
import com.tskhra.modulith.booking_module.repositories.*;
import com.tskhra.modulith.common.exception.custom_status_exceptions.CustomStatusException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpForbiddenError;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.common.model.enums.MyCustomStatus;
import com.tskhra.modulith.common.services.ImageService;
import com.tskhra.modulith.user_module.services.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class BusinessService {

    private final BusinessRepository businessRepository;
    private final CityRepository cityRepository;
    private final AddressRepository addressRepository;
    private final CategoryRepository categoryRepository;
    private final BusinessImageRepository businessImageRepository;
    private final BusinessScheduleRepository businessScheduleRepository;
    private final BusinessUnavailableScheduleRepository businessUnavailableScheduleRepository;
    private final ServiceRepository serviceRepository;
    private final ResourceRepository resourceRepository;
    private final BookingRepository bookingRepository;

    private final UserService userService;
    private final ImageService imageService;


    private static final int MAX_BUSINESSES_PER_USER = 5;
    public static final int SLOT_INTERVAL_MINUTES = 10;

    @Transactional
    public Long register(@Valid BusinessRegistrationDto dto, Jwt jwt) {
        LocalDateTime now = LocalDateTime.now();
        Long userId = userService.getCurrentUser(jwt).getId();

        long activeBusinessCount = businessRepository.countByUserIdAndActivityStatus(userId, ActivityStatus.ACTIVE);
        long inactiveBusinessCount = businessRepository.countByUserIdAndActivityStatus(userId, ActivityStatus.INACTIVE);

        log.info("Active business count: {}, Inactive business count: {}", activeBusinessCount, inactiveBusinessCount);

        // TODO write one query to simplify
        if (activeBusinessCount + inactiveBusinessCount >= MAX_BUSINESSES_PER_USER) {
            throw new CustomStatusException(MyCustomStatus.BUSINESS_NUMBER_LIMIT_REACHED, "A user can have at most " + MAX_BUSINESSES_PER_USER + " businesses");
        }

        if (dto.callType() != CallType.OUTCALL && dto.addressDetails().isBlank()) {
            throw new HttpBadRequestException("Address details must be present.");
        }

        Business business = Business.builder()
                .name(dto.businessName())
                .nameKa(dto.businessNameKa())
                .userId(userId)
                .description(dto.description())
                .descriptionKa(dto.descriptionKa())
                .phoneNumber(dto.info().phoneNumber())
                .instagramUrl(dto.info().instagramUrl())
                .facebookUrl(dto.info().facebookUrl())
                .businessType(BusinessType.INDIVIDUAL)
                .activityStatus(ActivityStatus.ACTIVE)
                .callType(dto.callType())
                .modificationDetails(new ModificationDetails(userId, userId, now, now))
                .build();

        Business savedBusiness = businessRepository.save(business);

//        Address
        Long cityId = dto.cityId();
        City city = cityRepository.findById(cityId)
                .orElseThrow(() -> new HttpNotFoundException("No such city"));
        Address address = new Address();
        address.setCity(city);
        address.setDetails(dto.addressDetails());
        address.setDetailsKa(dto.addressDetailsKa());
        Address savedAddress = addressRepository.save(address);
        savedBusiness.setAddress(savedAddress);

//        Category
        String categoryName = dto.subCategory();
        Category category = categoryRepository.findByName(categoryName)
                .orElseThrow(() -> new HttpNotFoundException("No such category: " + categoryName));
        savedBusiness.setCategory(category);

//        Work Times
        dto.workTimes().stream()
                .map(interval -> new BusinessSchedule(null, savedBusiness, interval))
                .forEach(businessScheduleRepository::save);

//        Rest Times
        if (dto.restTimes() != null) {
            dto.restTimes().stream()
                    .map(interval -> new BusinessUnavailableSchedule(null, savedBusiness, interval))
                    .forEach(businessUnavailableScheduleRepository::save);
        }

//        Single resource for individual business
        Resource resource = new Resource();
        resource.setBusiness(savedBusiness);
        resource.setName("self");
        resource.setActivityStatus(ActivityStatus.ACTIVE);
        resourceRepository.save(resource);

        return savedBusiness.getId();
    }

    public List<BusinessDetailsDto> getCurrentUserBusinesses(Lang lang, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();


        List<Business> businesses = businessRepository.findByUserId(userId);
        return businesses.stream()
                .filter(b -> b.getActivityStatus() != ActivityStatus.DELETED)
                .map(b -> mapToDto(b, lang))
                .toList();
    }

    public Page<BusinessDetailsDto> getAllBusinessPage(Pageable pageable) {
        Page<Business> businesses = businessRepository.findAllByActivityStatus(ActivityStatus.ACTIVE, pageable);
        return businesses.map(this::mapToDto);
    }

    public BusinessDetailsDto getSpecificBusiness(Long businessId) {
        Business b = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE).orElseThrow(
                () -> new HttpNotFoundException("Business not found with id: " + businessId)
        );
        return mapToDto(b);
    }

    private BusinessDetailsDto mapToDto(Business b) {
        return new BusinessDetailsDto(
                b.getId().toString(),
                b.getName(),
                b.getCategory() == null || b.getCategory().getParent() == null ? null : b.getCategory().getParent().getName(),
                b.getCategory() == null ? null : b.getCategory().getName(),
                imageService.getBusinessImageUrl(
                        b.getBusinessImages().stream()
                                .filter(BusinessImage::isMain)
                                .findFirst()
                                .map(BusinessImage::getFilename)
                                .orElse(null)
                ),
                b.getBusinessImages().stream()
                        .filter(bi -> !bi.isMain())
                        .map(BusinessImage::getFilename)
                        .map(imageService::getBusinessImageUrl)
                        .toList(),
                b.getAddress() == null ? null : b.getAddress().getCity().getName(),
                b.getAddress() == null ? null : b.getAddress().getDetails(),
                b.getCallType(),
                b.getBusinessSchedules().stream().map(BusinessSchedule::getInterval).toList(),
                b.getBusinessUnavailableSchedules().stream().map(BusinessUnavailableSchedule::getInterval).toList(),
                new Info(b.getPhoneNumber(), b.getInstagramUrl(), b.getFacebookUrl()),
                b.getDescription()
        );
    }

    private BusinessDetailsDto mapToDto(Business b, Lang lang) {
        String name = switch (lang) {
            case KA -> b.getNameKa() == null ? b.getName() : b.getNameKa();
            case EN -> b.getName();
        };
        String description = switch (lang) {
            case KA -> b.getDescriptionKa() == null ? b.getDescription() : b.getDescriptionKa();
            case EN -> b.getDescription();
        };
        String addressDetails = b.getAddress() == null ? null : switch (lang) {
            case KA -> b.getAddress().getDetailsKa() == null ? b.getAddress().getDetails() : b.getAddress().getDetailsKa();
            case EN -> b.getAddress().getDetails();
        };
        return new BusinessDetailsDto(
                b.getId().toString(),
                name,
                b.getCategory() == null || b.getCategory().getParent() == null ? null : b.getCategory().getParent().getName(),
                b.getCategory() == null ? null : b.getCategory().getName(),
                imageService.getBusinessImageUrl(
                        b.getBusinessImages().stream()
                                .filter(BusinessImage::isMain)
                                .findFirst()
                                .map(BusinessImage::getFilename)
                                .orElse(null)
                ),
                b.getBusinessImages().stream()
                        .filter(bi -> !bi.isMain())
                        .map(BusinessImage::getFilename)
                        .map(imageService::getBusinessImageUrl)
                        .toList(),
                b.getAddress() == null ? null : b.getAddress().getCity().getName(),
                addressDetails,
                b.getCallType(),
                b.getBusinessSchedules().stream().map(BusinessSchedule::getInterval).toList(),
                b.getBusinessUnavailableSchedules().stream().map(BusinessUnavailableSchedule::getInterval).toList(),
                new Info(b.getPhoneNumber(), b.getInstagramUrl(), b.getFacebookUrl()),
                description
        );
    }

    @Transactional
    public BusinessDetailsDto updateBusiness(Long businessId, BusinessUpdateDto dto, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Business business = businessRepository.findById(businessId).orElseThrow(
                () -> new HttpNotFoundException("Business not found with id: " + businessId)
        );

        if (!business.getUserId().equals(userId)) {
            throw new HttpForbiddenError("You are not authorized to update this business");
        }

        business.setName(dto.businessName());
        business.setCallType(dto.callType());
        business.setDescription(dto.description());
        business.setPhoneNumber(dto.info().phoneNumber());
        business.setInstagramUrl(dto.info().instagramUrl());
        business.setFacebookUrl(dto.info().facebookUrl());
        business.getModificationDetails().setUpdatedBy(userId);

        Business saved = businessRepository.save(business);
        return mapToDto(saved);
    }

    @Transactional
    public void deleteBusiness(Long businessId, Jwt jwt) {
        Business business = businessRepository.findById(businessId).orElseThrow(
                () -> new HttpNotFoundException("Business not found")
        );

        Long userId = userService.getCurrentUser(jwt).getId();
        if (!business.getUserId().equals(userId)) {
            throw new HttpForbiddenError("You are not authorized to delete this business");
        }

        business.setActivityStatus(ActivityStatus.DELETED);

        business.getServices().forEach(s -> s.setActivityStatus(ActivityStatus.DELETED));
        business.getResources().forEach(r -> r.setActivityStatus(ActivityStatus.DELETED));

        businessRepository.save(business);
    }

    public List<Integer> getAvailableStartTimes(Long businessId, TimeslotRequest request) {
        log.info("Fetching available timeslots for businessId: {}, serviceId: {}, date: {}",
                businessId, request.serviceId(), request.date());

        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE)
                .orElseThrow(() -> new HttpNotFoundException("Business not found"));

        com.tskhra.modulith.booking_module.model.domain.Service service =
                serviceRepository.findByIdAndActivityStatus(Long.valueOf(request.serviceId()), ActivityStatus.ACTIVE)
                        .orElseThrow(() -> new HttpNotFoundException("Service not found"));

        int duration = service.getSessionDuration();
        log.info("Service duration: {} minutes", duration);

        LocalDate date = request.date();
        Optional<WeekTimeInterval> workingHoursOptional = business.getBusinessSchedules().stream()
                .map(BusinessSchedule::getInterval)
                .filter(interval -> interval.getWeekDay() == WeekDay.from(date.getDayOfWeek()))
                .findFirst();

        Optional<WeekTimeInterval> restHoursOptional = business.getBusinessUnavailableSchedules().stream()
                .map(BusinessUnavailableSchedule::getInterval)
                .filter(interval -> interval.getWeekDay() == WeekDay.from(date.getDayOfWeek()))
                .findFirst();

        log.info("Working hours: {}, Rest hours: {}",
                workingHoursOptional.map(WeekTimeInterval::toString).orElse("None"),
                restHoursOptional.map(WeekTimeInterval::toString).orElse("None"));

        List<Booking> existingBookings = bookingRepository.findByBusinessIdAndDateAndStatuses(
                businessId, date, List.of(BookingStatus.AWAITING, BookingStatus.SCHEDULED)
        );

        log.info("Found {} existing bookings for date: {}", existingBookings.size(), date);

        boolean isToday = LocalDate.now().isEqual(date);

        log.info("Is today: {}", isToday);

        List<Integer> timeslots = workingHoursOptional.map(weekTimeInterval ->
                        generateTimeslots(weekTimeInterval, restHoursOptional, existingBookings, duration, SLOT_INTERVAL_MINUTES, isToday))
                .orElseGet(List::of);

        log.info("Generated {} available timeslots", timeslots.size());
        return timeslots;
    }

    private List<Integer> generateTimeslots(WeekTimeInterval weekTimeInterval, Optional<WeekTimeInterval> restHoursOptional, List<Booking> existingBookings, int duration, int slotIntervalMinutes, boolean today) {
        int start = weekTimeInterval.getStartTime();
        int end = weekTimeInterval.getEndTime();

        log.info("Generating timeslots from {} to {} with {} minute interval", start, end, slotIntervalMinutes);

        List<Integer> availableTimeslots = new ArrayList<>();
        for (int startTime = start; startTime <= end; startTime += slotIntervalMinutes) {
            int endTime = startTime + duration;
            int finalStartTime = startTime;

            boolean withinSchedule = start <= startTime && endTime <= end;
            if (!withinSchedule) {
                log.debug("Timeslot {}:{} skipped - outside working hours", startTime, endTime);
                continue;
            }

            boolean overlapsRest = restHoursOptional.map(restInterval ->
                            finalStartTime < restInterval.getEndTime() && restInterval.getStartTime() < endTime)
                    .orElse(false);
            if (overlapsRest) {
                log.debug("Timeslot {}:{} skipped - overlaps with rest hours", startTime, endTime);
                continue;
            }

            boolean overlapsBookings = existingBookings.stream()
                    .anyMatch(b -> finalStartTime < (b.getStartTime() + b.getDuration()) && b.getStartTime() < endTime);
            if (overlapsBookings) {
                log.debug("Timeslot {}:{} skipped - overlaps with existing booking", startTime, endTime);
                continue;
            }

            availableTimeslots.add(startTime);
        }


        log.info("Total available timeslots generated: {}", availableTimeslots.size());
        if (today) {

            LocalDateTime now = LocalDateTime.now();
            int currentTimeMinutes = now.getMinute() + now.getHour() * 60;
            log.info("Current time: {} minutes", currentTimeMinutes);
            return availableTimeslots.stream().filter(t -> t > currentTimeMinutes).toList();
        } else {
            return availableTimeslots;
        }

    }

    public void addImageToBusiness(Long businessId, Long imageId, boolean isMain) {
        Business business = businessRepository.findByIdAndActivityStatus(businessId, ActivityStatus.ACTIVE)
                .orElseThrow(() -> new HttpNotFoundException("Business not found"));

        BusinessImage image = businessImageRepository.findById(imageId)
                .orElseThrow(() -> new HttpNotFoundException("Image not found"));

        if (image.getBusiness() != null) {
            throw new HttpBadRequestException("Image is already assigned to a business");
        }

        if (businessImageRepository.countBusinessImageByBusiness(business) >= 5) {
            throw new HttpBadRequestException("Business can have at most 5 images");
        }

        if (isMain) {
            business.getBusinessImages().stream()
                    .filter(BusinessImage::isMain)
                    .forEach(bi -> bi.setMain(false));
        }

        image.setBusiness(business);
        image.setMain(isMain);
        businessImageRepository.save(image);
    }
}
