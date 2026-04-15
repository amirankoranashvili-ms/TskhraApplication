package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.domain.TradeOffer;
import com.tskhra.modulith.trade_module.model.requests.TradeOfferCreationDto;
import com.tskhra.modulith.trade_module.model.responses.OfferCreatedDto;
import com.tskhra.modulith.trade_module.services.TradeService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/trade-offers")
@RequiredArgsConstructor
public class TradeController {

    private final TradeService tradeService;

    @PostMapping
    public ResponseEntity<OfferCreatedDto> offerTrade(@Valid @RequestBody TradeOfferCreationDto dto,
                                                      @AuthenticationPrincipal Jwt jwt) {
        TradeOffer offer = tradeService.createOffer(dto, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(new OfferCreatedDto(offer.getId().toString()));
    }

    @PatchMapping("/{offerId}/accept")
    public ResponseEntity<Void> acceptOffer(@PathVariable UUID offerId,
                                            @AuthenticationPrincipal Jwt jwt) {
        tradeService.acceptOffer(offerId, jwt);
        return ResponseEntity.noContent().build();
    }

    @PatchMapping("/{offerId}/reject")
    public ResponseEntity<Void> rejectOffer(@PathVariable UUID offerId,
                                            @AuthenticationPrincipal Jwt jwt) {
        tradeService.rejectOffer(offerId, jwt);
        return ResponseEntity.noContent().build();
    }

    @PatchMapping("/{offerId}/withdraw")
    public ResponseEntity<Void> withdrawOffer(@PathVariable UUID offerId,
                                              @AuthenticationPrincipal Jwt jwt) {
        tradeService.withdrawOffer(offerId, jwt);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/{offerId}/counter")
    public ResponseEntity<OfferCreatedDto> counterOffer(@PathVariable UUID offerId,
                                                        @Valid @RequestBody TradeOfferCreationDto dto,
                                                        @AuthenticationPrincipal Jwt jwt) {
        TradeOffer counter = tradeService.counterOffer(offerId, dto, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(new OfferCreatedDto(counter.getId().toString()));
    }

    @PatchMapping("/{offerId}/cancel")
    public ResponseEntity<Void> cancelOffer(@PathVariable UUID offerId,
                                            @AuthenticationPrincipal Jwt jwt) {
        tradeService.cancelOffer(offerId, jwt);
        return ResponseEntity.noContent().build();
    }

    @PatchMapping("/{offerId}/confirm")
    public ResponseEntity<Void> confirmHandoff(@PathVariable UUID offerId,
                                               @AuthenticationPrincipal Jwt jwt) {
        tradeService.confirmHandoff(offerId, jwt);
        return ResponseEntity.noContent().build();
    }

}
