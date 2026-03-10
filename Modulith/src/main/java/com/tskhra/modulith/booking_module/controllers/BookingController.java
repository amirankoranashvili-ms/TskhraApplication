package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.requests.IndividualBookingRequest;
import com.tskhra.modulith.booking_module.services.BookingService;
import io.swagger.v3.oas.annotations.Operation;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/bookings")
@RequiredArgsConstructor
public class BookingController {

    private final BookingService bookingService;

    @Operation(summary = "User Books an individual service")
    @PostMapping("/individual")
    public ResponseEntity<Void> createBooking(@AuthenticationPrincipal Jwt jwt,
                                              @Valid @RequestBody IndividualBookingRequest request) {
        bookingService.createBooking(request, jwt);
        return new ResponseEntity<>(HttpStatus.CREATED);
    }

    @Operation(summary = "Business Owner Approves a booking request")
    @PostMapping("/{id}/approve")
    public ResponseEntity<Void> approveRequest(@PathVariable Long id,
                                               @AuthenticationPrincipal Jwt jwt) {
        bookingService.approveRequest(id, jwt);
        return new ResponseEntity<>(HttpStatus.OK);
    }

    @Operation(summary = "Business Owner Rejects a booking request")
    @PostMapping("/{id}/reject")
    public ResponseEntity<Void> rejectRequest(@PathVariable Long id,
                                              @AuthenticationPrincipal Jwt jwt) {
        bookingService.rejectRequest(id, jwt);
        return new ResponseEntity<>(HttpStatus.OK);
    }

    @Operation(summary = "Business Owner Cancels a booking request")
    @PostMapping("/{id}/cancel-by-business")
    public ResponseEntity<Void> cancelRequestBusiness(@PathVariable Long id,
                                              @AuthenticationPrincipal Jwt jwt) {
        bookingService.cancelByBusiness(id, jwt);
        return new ResponseEntity<>(HttpStatus.OK);
    }

    @Operation(summary = "Client Cancels a booking request")
    @PostMapping("/{id}/cancel")
    public ResponseEntity<Void> cancelRequest(@PathVariable Long id,
                                              @AuthenticationPrincipal Jwt jwt) {
        bookingService.cancelByUser(id, jwt);
        return new ResponseEntity<>(HttpStatus.OK);
    }




}
