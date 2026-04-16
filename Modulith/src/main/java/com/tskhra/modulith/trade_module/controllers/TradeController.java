package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.domain.TradeOffer;
import com.tskhra.modulith.trade_module.model.requests.TradeOfferCreationDto;
import com.tskhra.modulith.trade_module.model.responses.OfferCreatedDto;
import com.tskhra.modulith.trade_module.services.TradeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@Tag(name = "Trade Offers", description = "Trade offer lifecycle: create, accept, reject, counter, withdraw, cancel, confirm")
@RestController
@RequestMapping("/trade-offers")
@RequiredArgsConstructor
public class TradeController {

    private final TradeService tradeService;

    @Operation(summary = "Create a trade offer (status: PENDING, expires in 48h)")
    @PostMapping
    public ResponseEntity<OfferCreatedDto> offerTrade(@Valid @RequestBody TradeOfferCreationDto dto,
                                                      @AuthenticationPrincipal Jwt jwt) {
        TradeOffer offer = tradeService.createOffer(dto, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(new OfferCreatedDto(offer.getId().toString()));
    }

    @Operation(summary = "Responder accepts offer (items lock to IN_TRADE, conflicting offers auto-rejected)")
    @PutMapping("/{offerId}/accept")
    public ResponseEntity<Void> acceptOffer(@PathVariable UUID offerId,
                                            @AuthenticationPrincipal Jwt jwt) {
        tradeService.acceptOffer(offerId, jwt);
        return ResponseEntity.noContent().build();
    }

    @Operation(summary = "Responder rejects a PENDING offer")
    @PutMapping("/{offerId}/reject")
    public ResponseEntity<Void> rejectOffer(@PathVariable UUID offerId,
                                            @AuthenticationPrincipal Jwt jwt) {
        tradeService.rejectOffer(offerId, jwt);
        return ResponseEntity.noContent().build();
    }

    @Operation(summary = "Offerer withdraws their own PENDING offer")
    @PutMapping("/{offerId}/withdraw")
    public ResponseEntity<Void> withdrawOffer(@PathVariable UUID offerId,
                                              @AuthenticationPrincipal Jwt jwt) {
        tradeService.withdrawOffer(offerId, jwt);
        return ResponseEntity.noContent().build();
    }

    @Operation(summary = "Responder counters with a new offer (original becomes COUNTERED)")
    @PostMapping("/{offerId}/counter")
    public ResponseEntity<OfferCreatedDto> counterOffer(@PathVariable UUID offerId,
                                                        @Valid @RequestBody TradeOfferCreationDto dto,
                                                        @AuthenticationPrincipal Jwt jwt) {
        TradeOffer counter = tradeService.counterOffer(offerId, dto, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(new OfferCreatedDto(counter.getId().toString()));
    }

    @Operation(summary = "Either party cancels an ACCEPTED offer (items released back to AVAILABLE)")
    @PutMapping("/{offerId}/cancel")
    public ResponseEntity<Void> cancelOffer(@PathVariable UUID offerId,
                                            @AuthenticationPrincipal Jwt jwt) {
        tradeService.cancelOffer(offerId, jwt);
        return ResponseEntity.noContent().build();
    }

    @Operation(summary = "Confirm item handoff (both parties must confirm to complete the trade)")
    @PutMapping("/{offerId}/confirm")
    public ResponseEntity<Void> confirmHandoff(@PathVariable UUID offerId,
                                               @AuthenticationPrincipal Jwt jwt) {
        tradeService.confirmHandoff(offerId, jwt);
        return ResponseEntity.noContent().build();
    }

}
