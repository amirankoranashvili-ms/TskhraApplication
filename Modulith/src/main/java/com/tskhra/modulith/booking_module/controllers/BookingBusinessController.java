package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.enums.Lang;
import com.tskhra.modulith.booking_module.model.responses.BookingDto;
import com.tskhra.modulith.booking_module.services.BookingService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/business")
@RequiredArgsConstructor
public class BookingBusinessController {

    private final BookingService bookingService;

    @GetMapping("/{id}/bookings/awaiting")
    public ResponseEntity<List<BookingDto>> getAwaitingBookingsForBusiness(@PathVariable("id") Long businessId,
                                                                           @RequestParam(defaultValue = "EN") Lang lang,
                                                                           @AuthenticationPrincipal Jwt jwt) {
        List<BookingDto> awaitingBookings = bookingService.getAwaitingBookings(businessId, lang, jwt);
        return ResponseEntity.ok(awaitingBookings);
    }

    @GetMapping("/{id}/bookings/scheduled")
    public ResponseEntity<List<BookingDto>> getScheduledBookingsForBusiness(@PathVariable("id") Long businessId,
                                                                            @RequestParam(defaultValue = "EN") Lang lang,
                                                                            @AuthenticationPrincipal Jwt jwt) {
        List<BookingDto> awaitingBookings = bookingService.getScheduledBookings(businessId, lang, jwt);
        return ResponseEntity.ok(awaitingBookings);
    }

    // for testing jenkins 3
}
