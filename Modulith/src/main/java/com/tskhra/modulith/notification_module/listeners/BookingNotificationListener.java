package com.tskhra.modulith.notification_module.listeners;

import com.tskhra.modulith.booking_module.model.enums.BookingStatus;
import com.tskhra.modulith.booking_module.model.events.BookingStatusChangedEvent;
import com.tskhra.modulith.notification_module.services.FcmNotificationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class BookingNotificationListener {

    private final FcmNotificationService fcmNotificationService;

    @Async
    @EventListener
    public void onBookingStatusChanged(BookingStatusChangedEvent event) {
        log.info("Received BookingStatusChangedEvent: bookingId={}, recipientUserId={}, status={}, service={}, business={}",
                event.bookingId(), event.recipientUserId(), event.newStatus(), event.serviceName(), event.businessName());

        String title = buildTitle(event.newStatus());
        String body = buildBody(event.newStatus(), event.serviceName(), event.businessName());

        Map<String, String> data = Map.of(
                "bookingId", event.bookingId().toString(),
                "status", event.newStatus().name()
        );

        log.info("Sending FCM notification: title='{}', body='{}', data={}", title, body, data);
        fcmNotificationService.sendToUser(event.recipientUserId(), title, body, data);
    }

    private String buildTitle(BookingStatus status) {
        return switch (status) {
            case AWAITING -> "New Booking Request";
            case SCHEDULED -> "Booking Accepted";
            case REJECTED -> "Booking Rejected";
            case CANCELLED_BY_BUSINESS -> "Booking Cancelled";
            case CANCELLED_BY_USER -> "Booking Cancelled";
            case COMPLETED -> "Booking Completed";
        };
    }

    private String buildBody(BookingStatus status, String serviceName, String businessName) {
        return switch (status) {
            case AWAITING -> "New booking request for " + serviceName;
            case SCHEDULED -> "Your booking for " + serviceName + " at " + businessName + " has been accepted";
            case REJECTED -> "Your booking for " + serviceName + " at " + businessName + " has been rejected";
            case CANCELLED_BY_BUSINESS -> "Your booking for " + serviceName + " at " + businessName + " has been cancelled";
            case CANCELLED_BY_USER -> "Booking for " + serviceName + " has been cancelled by the customer";
            case COMPLETED -> "Your booking for " + serviceName + " at " + businessName + " is completed";
        };
    }
}
