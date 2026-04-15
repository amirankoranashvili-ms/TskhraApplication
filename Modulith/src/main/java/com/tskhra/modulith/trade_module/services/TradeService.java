package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.domain.OfferItem;
import com.tskhra.modulith.trade_module.model.domain.TradeOffer;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.enums.OwningSide;
import com.tskhra.modulith.trade_module.model.enums.TradeStatus;
import com.tskhra.modulith.trade_module.model.requests.TradeOfferCreationDto;
import com.tskhra.modulith.trade_module.repositories.ItemRepository;
import com.tskhra.modulith.trade_module.repositories.OfferItemRepository;
import com.tskhra.modulith.trade_module.repositories.TradeOfferRepository;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;
import java.util.stream.Stream;

@Service
@RequiredArgsConstructor
public class TradeService {

    private final UserService userService;
    private final ItemRepository itemRepository;
    private final TradeOfferRepository tradeOfferRepository;

    @Transactional
    public TradeOffer createOffer(TradeOfferCreationDto dto, Jwt jwt) {
        Long offererId = userService.getCurrentUser(jwt).getId();
        Long responderId = dto.responderId();

        if (Objects.equals(offererId, responderId)) {
            throw new HttpBadRequestException("Offerer and responder cannot be the same user");
        }

        // Check for duplicate item IDs
        Set<UUID> allItemIds = new HashSet<>();
        allItemIds.addAll(dto.offererItems());
        allItemIds.addAll(dto.responderItems());
        if (allItemIds.size() != dto.offererItems().size() + dto.responderItems().size()) {
            throw new HttpBadRequestException("Duplicate items are not allowed");
        }

        List<Item> offererItems = itemRepository.findAllById(dto.offererItems());
        if (offererItems.size() != dto.offererItems().size()) {
            throw new HttpBadRequestException("One or more offerer items not found");
        }

        List<Item> responderItems = itemRepository.findAllById(dto.responderItems());
        if (responderItems.size() != dto.responderItems().size()) {
            throw new HttpBadRequestException("One or more responder items not found");
        }

        // Verify ownership
        boolean offererItemsBelongToOfferer = offererItems.stream()
                .allMatch(item -> Objects.equals(item.getOwnerId(), offererId));
        if (!offererItemsBelongToOfferer) {
            throw new HttpBadRequestException("Offerer items must belong to the offerer");
        }

        boolean responderItemsBelongToResponder = responderItems.stream()
                .allMatch(item -> Objects.equals(item.getOwnerId(), responderId));
        if (!responderItemsBelongToResponder) {
            throw new HttpBadRequestException("Responder items must belong to the responder");
        }

        // Verify all items are available
        boolean allAvailable = Stream.concat(offererItems.stream(), responderItems.stream())
                .allMatch(item -> item.getStatus() == ItemStatus.AVAILABLE);
        if (!allAvailable) {
            throw new HttpBadRequestException("All items must be in AVAILABLE status");
        }

        // Build offer
        TradeOffer tradeOffer = TradeOffer.builder()
                .offererId(offererId)
                .responderId(responderId)
                .status(TradeStatus.PENDING)
                .build();

        List<OfferItem> offerItems = Stream.concat(
                offererItems.stream()
                        .map(i -> new OfferItem(i, tradeOffer, OwningSide.OFFERER)),
                responderItems.stream()
                        .map(i -> new OfferItem(i, tradeOffer, OwningSide.RESPONDER))
        ).toList();

        tradeOffer.setOfferItems(offerItems);
        tradeOffer.setFairnessRatio(calculateFairnessRatio(offererItems, responderItems));

        return tradeOfferRepository.save(tradeOffer);
    }

    private BigDecimal calculateFairnessRatio(List<Item> offererItems, List<Item> responderItems) {
        BigDecimal offererTotal = offererItems.stream()
                .map(Item::getEstimatedValue)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        BigDecimal responderTotal = responderItems.stream()
                .map(Item::getEstimatedValue)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        BigDecimal higher = offererTotal.max(responderTotal);
        BigDecimal lower = offererTotal.min(responderTotal);

        if (higher.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ONE;
        }

        return lower.divide(higher, 2, RoundingMode.HALF_UP);
    }
}
