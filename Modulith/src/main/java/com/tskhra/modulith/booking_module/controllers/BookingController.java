package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.requests.IndividualBookingRequest;
import com.tskhra.modulith.booking_module.services.BookingService;
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
@RequestMapping("/bookings")
@RequiredArgsConstructor
public class BookingController {

    private final BookingService bookingService;

    @PostMapping("/individual")
    public ResponseEntity<Void> createBooking(@AuthenticationPrincipal Jwt jwt,
                                              @RequestBody IndividualBookingRequest request) {
        bookingService.createBooking(request, jwt);
        return new ResponseEntity<>(HttpStatus.CREATED);
    }

}
