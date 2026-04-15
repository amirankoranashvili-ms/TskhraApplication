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
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/trade-offers")
@RequiredArgsConstructor
public class TradeController {

    private final TradeService tradeService;

    @PostMapping
    public ResponseEntity<OfferCreatedDto> offerTrade(@Valid @RequestBody TradeOfferCreationDto dto,
                                                      @AuthenticationPrincipal Jwt jwt) {
        TradeOffer offer = tradeService.createOffer(dto, jwt);
        return ResponseEntity.ok(new OfferCreatedDto(offer.getId().toString()));
    }

}
