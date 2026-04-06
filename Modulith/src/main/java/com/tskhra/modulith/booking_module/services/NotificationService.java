package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.Business;
import com.tskhra.modulith.booking_module.model.enums.BookingStatus;
import com.tskhra.modulith.booking_module.repositories.BookingRepository;
import com.tskhra.modulith.booking_module.repositories.BusinessRepository;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@Slf4j
@RequiredArgsConstructor
public class NotificationService {

    private final BookingRepository bookingRepository;
    private final BusinessRepository businessRepository;
    private final UserService userService;
    private final BusinessService businessService;


    public int getNotificationCountByUser(Jwt jwt) {
        Long businessOwnerId = userService.getCurrentUser(jwt).getId();

        return businessRepository.findByUserId(businessOwnerId).stream()
                .map(Business::getId)
                .peek(id -> log.info("Business id: {}", id))
                .mapToInt(businessService::getBusinessAwaitingBookingCount)
                .peek(num -> log.info("Number of bookings: {}", num))
                .sum();
    }
}
