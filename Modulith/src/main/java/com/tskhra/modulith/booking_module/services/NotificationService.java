package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.Business;
import com.tskhra.modulith.booking_module.model.enums.BookingStatus;
import com.tskhra.modulith.booking_module.repositories.BookingRepository;
import com.tskhra.modulith.booking_module.repositories.BusinessRepository;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class NotificationService {

    private final BookingRepository bookingRepository;
    private final BusinessRepository businessRepository;
    private final UserService userService;


    public int getNotificationCountByUser(Jwt jwt) {
        Long businessOwnerId = userService.getCurrentUser(jwt).getId();
        List<Long> businessIds = businessRepository
                .findByUserId(businessOwnerId).stream().map(Business::getId).toList();

        return bookingRepository.countByBusinessIdsAndStatus(businessIds, BookingStatus.AWAITING);
    }
}
