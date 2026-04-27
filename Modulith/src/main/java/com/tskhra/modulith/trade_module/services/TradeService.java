package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpForbiddenError;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.domain.OfferItem;
import com.tskhra.modulith.trade_module.model.domain.TradeOffer;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.enums.OwningSide;
import com.tskhra.modulith.trade_module.model.enums.TradeStatus;
import com.tskhra.modulith.trade_module.model.events.ItemStatusChangedEvent;
import com.tskhra.modulith.trade_module.model.requests.TradeOfferCreationDto;
import com.tskhra.modulith.trade_module.model.domain.ItemImage;
import com.tskhra.modulith.trade_module.model.enums.OfferDirection;
import com.tskhra.modulith.trade_module.model.responses.TradeOfferSummaryDto;
import com.tskhra.modulith.trade_module.elastic.services.ItemSearchService;
import com.tskhra.modulith.trade_module.repositories.ItemRepository;
import com.tskhra.modulith.trade_module.repositories.TradeOfferRepository;
import com.tskhra.modulith.common.services.ImageService;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Stream;

@Service
@RequiredArgsConstructor
public class TradeService {

    private static final long PENDING_EXPIRY_HOURS = 48;
    private static final long CONFIRMATION_EXPIRY_HOURS = 72;

    private final UserService userService;
    private final ImageService imageService;
    private final ItemSearchService itemSearchService;
    private final ItemRepository itemRepository;
    private final TradeOfferRepository tradeOfferRepository;
    private final ApplicationEventPublisher eventPublisher;

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
                .expiresAt(Instant.now().plus(PENDING_EXPIRY_HOURS, ChronoUnit.HOURS))
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

    @Transactional
    public void acceptOffer(UUID offerId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        TradeOffer offer = getOfferOrThrow(offerId);
        checkExpiry(offer);

        if (offer.getStatus() != TradeStatus.PENDING) {
            throw new HttpBadRequestException("Only PENDING offers can be accepted");
        }
        if (!offer.getResponderId().equals(userId)) {
            throw new HttpForbiddenError("Only the responder can accept an offer");
        }

        // Lock all items and verify availability
        List<UUID> itemIds = offer.getOfferItems().stream()
                .map(oi -> oi.getItem().getId())
                .toList();
        List<Item> lockedItems = itemRepository.findAllByIdForUpdate(itemIds);

        boolean allAvailable = lockedItems.stream()
                .allMatch(item -> item.getStatus() == ItemStatus.AVAILABLE);
        if (!allAvailable) {
            throw new HttpBadRequestException("One or more items are no longer available");
        }

        lockedItems.forEach(item -> {
            ItemStatus oldStatus = item.getStatus();
            item.setStatus(ItemStatus.IN_TRADE);
            itemSearchService.updateItemStatus(item.getId(), ItemStatus.IN_TRADE);
            eventPublisher.publishEvent(new ItemStatusChangedEvent(item.getId(), oldStatus, ItemStatus.IN_TRADE));
        });
        itemRepository.saveAll(lockedItems);

        // Accept offer
        offer.setStatus(TradeStatus.ACCEPTED);
        offer.setExpiresAt(Instant.now().plus(CONFIRMATION_EXPIRY_HOURS, ChronoUnit.HOURS));
        tradeOfferRepository.save(offer);

        // Auto-reject other PENDING offers involving these items
        List<TradeOffer> conflicting = tradeOfferRepository.findAllByItemIdsAndStatus(itemIds, TradeStatus.PENDING);
        conflicting.stream()
                .filter(o -> !o.getId().equals(offerId))
                .forEach(o -> o.setStatus(TradeStatus.REJECTED));
        tradeOfferRepository.saveAll(conflicting);
    }

    @Transactional
    public void rejectOffer(UUID offerId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        TradeOffer offer = getOfferOrThrow(offerId);
        checkExpiry(offer);

        if (offer.getStatus() != TradeStatus.PENDING) {
            throw new HttpBadRequestException("Only PENDING offers can be rejected");
        }
        if (!offer.getResponderId().equals(userId)) {
            throw new HttpForbiddenError("Only the responder can reject an offer");
        }

        offer.setStatus(TradeStatus.REJECTED);
        tradeOfferRepository.save(offer);
    }

    @Transactional
    public void withdrawOffer(UUID offerId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        TradeOffer offer = getOfferOrThrow(offerId);
        checkExpiry(offer);

        if (offer.getStatus() != TradeStatus.PENDING) {
            throw new HttpBadRequestException("Only PENDING offers can be withdrawn");
        }
        if (!offer.getOffererId().equals(userId)) {
            throw new HttpForbiddenError("Only the offerer can withdraw an offer");
        }

        offer.setStatus(TradeStatus.WITHDRAWN);
        tradeOfferRepository.save(offer);
    }

    @Transactional
    public TradeOffer counterOffer(UUID offerId, TradeOfferCreationDto dto, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        TradeOffer original = getOfferOrThrow(offerId);
        checkExpiry(original);

        if (original.getStatus() != TradeStatus.PENDING) {
            throw new HttpBadRequestException("Only PENDING offers can be countered");
        }
        if (!original.getResponderId().equals(userId)) {
            throw new HttpForbiddenError("Only the responder can counter an offer");
        }

        original.setStatus(TradeStatus.COUNTERED);
        tradeOfferRepository.save(original);

        // Create counter-offer with swapped roles
        TradeOffer counter = createOffer(dto, jwt);
        counter.setParent(original);
        return tradeOfferRepository.save(counter);
    }

    @Transactional
    public void cancelOffer(UUID offerId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        TradeOffer offer = getOfferOrThrow(offerId);
        checkExpiry(offer);

        if (offer.getStatus() != TradeStatus.ACCEPTED) {
            throw new HttpBadRequestException("Only ACCEPTED offers can be cancelled");
        }
        if (!offer.getOffererId().equals(userId) && !offer.getResponderId().equals(userId)) {
            throw new HttpForbiddenError("Only participants can cancel an offer");
        }

        offer.setStatus(TradeStatus.CANCELED);
        tradeOfferRepository.save(offer);

        releaseItems(offer);
    }

    @Transactional
    public void confirmHandoff(UUID offerId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        TradeOffer offer = getOfferOrThrow(offerId);
        checkExpiry(offer);

        if (offer.getStatus() != TradeStatus.ACCEPTED) {
            throw new HttpBadRequestException("Only ACCEPTED offers can be confirmed");
        }

        if (offer.getOffererId().equals(userId)) {
            if (offer.getOffererConfirmedAt() != null) {
                throw new HttpBadRequestException("You have already confirmed");
            }
            offer.setOffererConfirmedAt(LocalDateTime.now());
        } else if (offer.getResponderId().equals(userId)) {
            if (offer.getResponderConfirmedAt() != null) {
                throw new HttpBadRequestException("You have already confirmed");
            }
            offer.setResponderConfirmedAt(LocalDateTime.now());
        } else {
            throw new HttpForbiddenError("Only participants can confirm handoff");
        }

        // If both confirmed, complete the trade
        if (offer.getOffererConfirmedAt() != null && offer.getResponderConfirmedAt() != null) {
            offer.setStatus(TradeStatus.COMPLETED);
            offer.getOfferItems().stream()
                    .map(OfferItem::getItem)
                    .forEach(item -> {
                        item.setStatus(ItemStatus.TRADED);
                        itemSearchService.updateItemStatus(item.getId(), ItemStatus.TRADED);
                        eventPublisher.publishEvent(new ItemStatusChangedEvent(item.getId(), ItemStatus.IN_TRADE, ItemStatus.TRADED));
                    });
        }

        tradeOfferRepository.save(offer);
    }

    @Transactional(readOnly = true)
    public Page<TradeOfferSummaryDto> getCurrentUserOffers(Jwt jwt, OfferDirection direction, TradeStatus status, Pageable pageable) {
        Long userId = userService.getCurrentUser(jwt).getId();

        Page<TradeOffer> offers;
        if (direction == OfferDirection.SENT) {
            offers = status != null
                    ? tradeOfferRepository.findAllByOffererIdAndStatus(userId, status, pageable)
                    : tradeOfferRepository.findAllByOffererId(userId, pageable);
        } else if (direction == OfferDirection.RECEIVED) {
            offers = status != null
                    ? tradeOfferRepository.findAllByResponderIdAndStatus(userId, status, pageable)
                    : tradeOfferRepository.findAllByResponderId(userId, pageable);
        } else {
            offers = status != null
                    ? tradeOfferRepository.findAllByUserIdAndStatus(userId, status, pageable)
                    : tradeOfferRepository.findAllByUserId(userId, pageable);
        }

        return offers.map(this::toOfferSummaryDto);
    }

    private TradeOfferSummaryDto toOfferSummaryDto(TradeOffer offer) {
        List<TradeOfferSummaryDto.OfferItemDto> offererItems = offer.getOfferItems().stream()
                .filter(oi -> oi.getOwningSide() == OwningSide.OFFERER)
                .map(oi -> toOfferItemDto(oi.getItem()))
                .toList();

        List<TradeOfferSummaryDto.OfferItemDto> responderItems = offer.getOfferItems().stream()
                .filter(oi -> oi.getOwningSide() == OwningSide.RESPONDER)
                .map(oi -> toOfferItemDto(oi.getItem()))
                .toList();

        return new TradeOfferSummaryDto(
                offer.getId(),
                offer.getOffererId(),
                offer.getResponderId(),
                offer.getStatus(),
                offer.getFairnessRatio(),
                offer.getExpiresAt(),
                offererItems,
                responderItems,
                offer.getCreatedAt()
        );
    }

    private TradeOfferSummaryDto.OfferItemDto toOfferItemDto(Item item) {
        String firstImage = item.getImages().stream()
                .findFirst()
                .map(ItemImage::getUri)
                .map(imageService::getItemImageUrl)
                .orElse(null);

        return new TradeOfferSummaryDto.OfferItemDto(item.getId(), item.getName(), firstImage);
    }

    private TradeOffer getOfferOrThrow(UUID offerId) {
        return tradeOfferRepository.findById(offerId)
                .orElseThrow(() -> new HttpNotFoundException("Trade offer not found"));
    }

    private void checkExpiry(TradeOffer offer) {
        if (offer.getExpiresAt() != null
                && Instant.now().isAfter(offer.getExpiresAt())
                && (offer.getStatus() == TradeStatus.PENDING || offer.getStatus() == TradeStatus.ACCEPTED)) {

            if (offer.getStatus() == TradeStatus.ACCEPTED) {
                releaseItems(offer);
            }
            offer.setStatus(TradeStatus.EXPIRED);
            tradeOfferRepository.save(offer);
            throw new HttpBadRequestException("This offer has expired");
        }
    }

    private void releaseItems(TradeOffer offer) {
        List<Item> items = offer.getOfferItems().stream()
                .map(OfferItem::getItem)
                .toList();
        items.forEach(item -> {
            ItemStatus oldStatus = item.getStatus();
            item.setStatus(ItemStatus.AVAILABLE);
            itemSearchService.updateItemStatus(item.getId(), ItemStatus.AVAILABLE);
            eventPublisher.publishEvent(new ItemStatusChangedEvent(item.getId(), oldStatus, ItemStatus.AVAILABLE));
        });
        itemRepository.saveAll(items);
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
