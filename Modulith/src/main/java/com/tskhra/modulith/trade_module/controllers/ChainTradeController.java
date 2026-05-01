package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.model.enums.ChainStatus;
import com.tskhra.modulith.trade_module.model.requests.ChainDiscoverDto;
import com.tskhra.modulith.trade_module.model.requests.ChainProposalDto;
import com.tskhra.modulith.trade_module.model.responses.ChainCandidateDto;
import com.tskhra.modulith.trade_module.model.responses.ChainTradeSummaryDto;
import com.tskhra.modulith.trade_module.services.ChainTradeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@Tag(name = "Chain Trades", description = "Discover and manage chain trades")
@RestController
@RequestMapping("/chain-trades")
@RequiredArgsConstructor
public class ChainTradeController {

    private final ChainTradeService chainTradeService;

    @Operation(summary = "Discover chain trade opportunities for an item")
    @PostMapping("/discover")
    public ResponseEntity<List<ChainCandidateDto>> discover(@Valid @RequestBody ChainDiscoverDto dto,
                                                            @AuthenticationPrincipal Jwt jwt) {
        return ResponseEntity.ok(chainTradeService.discoverChains(dto.itemId(), 20, jwt));
    }

    @Operation(summary = "Propose a chain trade")
    @PostMapping
    public ResponseEntity<ChainTradeSummaryDto> propose(@Valid @RequestBody ChainProposalDto dto,
                                                        @AuthenticationPrincipal Jwt jwt) {
        return ResponseEntity.status(HttpStatus.CREATED).body(chainTradeService.proposeChain(dto, jwt));
    }

    @Operation(summary = "Get chain trade details")
    @GetMapping("/{chainId}")
    public ResponseEntity<ChainTradeSummaryDto> getDetails(@PathVariable UUID chainId,
                                                           @AuthenticationPrincipal Jwt jwt) {
        return ResponseEntity.ok(chainTradeService.getChainDetails(chainId, jwt));
    }

    @Operation(summary = "Accept participation in a chain trade")
    @PutMapping("/{chainId}/accept")
    public ResponseEntity<Void> accept(@PathVariable UUID chainId,
                                       @AuthenticationPrincipal Jwt jwt) {
        chainTradeService.acceptChain(chainId, jwt);
        return ResponseEntity.ok().build();
    }

    @Operation(summary = "Reject a chain trade (breaks the chain)")
    @PutMapping("/{chainId}/reject")
    public ResponseEntity<Void> reject(@PathVariable UUID chainId,
                                       @AuthenticationPrincipal Jwt jwt) {
        chainTradeService.rejectChain(chainId, jwt);
        return ResponseEntity.ok().build();
    }

    @Operation(summary = "Confirm handoff of your item in the chain")
    @PutMapping("/{chainId}/confirm")
    public ResponseEntity<Void> confirm(@PathVariable UUID chainId,
                                        @AuthenticationPrincipal Jwt jwt) {
        chainTradeService.confirmHandoff(chainId, jwt);
        return ResponseEntity.ok().build();
    }

    @Operation(summary = "List your chain trades")
    @GetMapping("/me")
    public ResponseEntity<Page<ChainTradeSummaryDto>> myChainTrades(@RequestParam(required = false) ChainStatus status,
                                                                    @RequestParam(defaultValue = "0") int page,
                                                                    @RequestParam(defaultValue = "20") int size,
                                                                    @AuthenticationPrincipal Jwt jwt) {
        return ResponseEntity.ok(chainTradeService.getMyChainTrades(jwt, status, PageRequest.of(page, size)));
    }

}
