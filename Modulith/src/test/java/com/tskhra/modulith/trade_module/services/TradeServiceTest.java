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
import com.tskhra.modulith.trade_module.model.requests.TradeOfferCreationDto;
import com.tskhra.modulith.trade_module.repositories.ItemRepository;
import com.tskhra.modulith.trade_module.repositories.TradeOfferRepository;
import com.tskhra.modulith.common.services.ImageService;
import com.tskhra.modulith.user_module.model.domain.User;
import com.tskhra.modulith.user_module.services.UserService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.oauth2.jwt.Jwt;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class TradeServiceTest {

    @Mock
    private UserService userService;

    @Mock
    private ImageService imageService;

    @Mock
    private ItemRepository itemRepository;

    @Mock
    private TradeOfferRepository tradeOfferRepository;

    @InjectMocks
    private TradeService tradeService;

    private static final Long OFFERER_ID = 1L;
    private static final Long RESPONDER_ID = 2L;
    private static final Long STRANGER_ID = 99L;

    private Jwt offererJwt;
    private Jwt responderJwt;
    private Jwt strangerJwt;

    @BeforeEach
    void setUp() {
        offererJwt = buildJwt();
        responderJwt = buildJwt();
        strangerJwt = buildJwt();

        lenient().when(userService.getCurrentUser(offererJwt)).thenReturn(buildUser(OFFERER_ID));
        lenient().when(userService.getCurrentUser(responderJwt)).thenReturn(buildUser(RESPONDER_ID));
        lenient().when(userService.getCurrentUser(strangerJwt)).thenReturn(buildUser(STRANGER_ID));
    }

    // ==================== createOffer ====================

    @Nested
    class CreateOffer {

        @Test
        void happyPath_createsOfferWithPendingStatus() {
            UUID itemA = UUID.randomUUID();
            UUID itemB = UUID.randomUUID();
            TradeOfferCreationDto dto = new TradeOfferCreationDto(RESPONDER_ID, List.of(itemA), List.of(itemB));

            Item offererItem = buildItem(itemA, OFFERER_ID, ItemStatus.AVAILABLE, new BigDecimal("100"));
            Item responderItem = buildItem(itemB, RESPONDER_ID, ItemStatus.AVAILABLE, new BigDecimal("80"));

            when(itemRepository.findAllById(List.of(itemA))).thenReturn(List.of(offererItem));
            when(itemRepository.findAllById(List.of(itemB))).thenReturn(List.of(responderItem));
            when(tradeOfferRepository.save(any(TradeOffer.class))).thenAnswer(inv -> {
                TradeOffer offer = inv.getArgument(0);
                offer.setId(UUID.randomUUID());
                return offer;
            });

            System.out.println("\n=== CREATE OFFER - Happy Path ===");
            System.out.println("Offerer (user " + OFFERER_ID + ") offering item " + itemA + " (value=100, status=AVAILABLE)");
            System.out.println("Responder (user " + RESPONDER_ID + ") item " + itemB + " (value=80, status=AVAILABLE)");

            TradeOffer result = tradeService.createOffer(dto, offererJwt);

            System.out.println("--- Result ---");
            System.out.println("Offer ID:       " + result.getId());
            System.out.println("Status:         " + result.getStatus());
            System.out.println("Offerer ID:     " + result.getOffererId());
            System.out.println("Responder ID:   " + result.getResponderId());
            System.out.println("Fairness Ratio: " + result.getFairnessRatio());
            System.out.println("Expires At:     " + result.getExpiresAt());
            System.out.println("Offer Items:    " + result.getOfferItems().size() + " items");
            result.getOfferItems().forEach(oi ->
                    System.out.println("  - Item " + oi.getItem().getId() + " | side=" + oi.getOwningSide() + " | owner=" + oi.getItem().getOwnerId()));

            assertEquals(TradeStatus.PENDING, result.getStatus());
            assertEquals(OFFERER_ID, result.getOffererId());
            assertEquals(RESPONDER_ID, result.getResponderId());
            assertNotNull(result.getExpiresAt());
            assertNotNull(result.getFairnessRatio());
            assertEquals(2, result.getOfferItems().size());
        }

        @Test
        void sameUserAsOffererAndResponder_throws() {
            System.out.println("\n=== CREATE OFFER - Same User as Offerer & Responder ===");
            System.out.println("User " + OFFERER_ID + " tries to trade with themselves");
            TradeOfferCreationDto dto = new TradeOfferCreationDto(OFFERER_ID, List.of(UUID.randomUUID()), List.of(UUID.randomUUID()));

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void duplicateItemIds_throws() {
            UUID sharedId = UUID.randomUUID();
            System.out.println("\n=== CREATE OFFER - Duplicate Item IDs ===");
            System.out.println("Same item " + sharedId + " appears in both offerer and responder lists");
            TradeOfferCreationDto dto = new TradeOfferCreationDto(RESPONDER_ID, List.of(sharedId), List.of(sharedId));

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void offererItemNotFound_throws() {
            UUID itemA = UUID.randomUUID();
            UUID itemB = UUID.randomUUID();
            System.out.println("\n=== CREATE OFFER - Offerer Item Not Found ===");
            System.out.println("Offerer item " + itemA + " does not exist in DB");
            TradeOfferCreationDto dto = new TradeOfferCreationDto(RESPONDER_ID, List.of(itemA), List.of(itemB));

            when(itemRepository.findAllById(List.of(itemA))).thenReturn(Collections.emptyList());

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void responderItemNotFound_throws() {
            UUID itemA = UUID.randomUUID();
            UUID itemB = UUID.randomUUID();
            System.out.println("\n=== CREATE OFFER - Responder Item Not Found ===");
            System.out.println("Responder item " + itemB + " does not exist in DB");
            TradeOfferCreationDto dto = new TradeOfferCreationDto(RESPONDER_ID, List.of(itemA), List.of(itemB));

            when(itemRepository.findAllById(List.of(itemA))).thenReturn(List.of(buildItem(itemA, OFFERER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN)));
            when(itemRepository.findAllById(List.of(itemB))).thenReturn(Collections.emptyList());

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void offererItemBelongsToWrongUser_throws() {
            UUID itemA = UUID.randomUUID();
            UUID itemB = UUID.randomUUID();
            System.out.println("\n=== CREATE OFFER - Offerer Item Belongs to Wrong User ===");
            System.out.println("User " + OFFERER_ID + " claims item " + itemA + " but it belongs to user " + STRANGER_ID);
            TradeOfferCreationDto dto = new TradeOfferCreationDto(RESPONDER_ID, List.of(itemA), List.of(itemB));

            when(itemRepository.findAllById(List.of(itemA))).thenReturn(List.of(buildItem(itemA, STRANGER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN)));
            when(itemRepository.findAllById(List.of(itemB))).thenReturn(List.of(buildItem(itemB, RESPONDER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN)));

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void itemNotAvailable_throws() {
            UUID itemA = UUID.randomUUID();
            UUID itemB = UUID.randomUUID();
            System.out.println("\n=== CREATE OFFER - Item Not Available ===");
            System.out.println("Item " + itemA + " has status IN_TRADE, not AVAILABLE");
            TradeOfferCreationDto dto = new TradeOfferCreationDto(RESPONDER_ID, List.of(itemA), List.of(itemB));

            when(itemRepository.findAllById(List.of(itemA))).thenReturn(List.of(buildItem(itemA, OFFERER_ID, ItemStatus.IN_TRADE, BigDecimal.TEN)));
            when(itemRepository.findAllById(List.of(itemB))).thenReturn(List.of(buildItem(itemB, RESPONDER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN)));

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }
    }

    // ==================== acceptOffer ====================

    @Nested
    class AcceptOffer {

        @Test
        void happyPath_setsAcceptedAndLocksItems() {
            UUID offerId = UUID.randomUUID();
            UUID itemAId = UUID.randomUUID();
            UUID itemBId = UUID.randomUUID();

            Item itemA = buildItem(itemAId, OFFERER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN);
            Item itemB = buildItem(itemBId, RESPONDER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN);
            TradeOffer offer = buildPendingOffer(offerId, itemA, itemB);

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));
            when(itemRepository.findAllByIdForUpdate(any())).thenReturn(List.of(itemA, itemB));
            when(tradeOfferRepository.findAllByItemIdsAndStatus(any(), eq(TradeStatus.PENDING))).thenReturn(Collections.emptyList());
            when(tradeOfferRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            System.out.println("\n=== ACCEPT OFFER - Happy Path ===");
            System.out.println("Offer " + offerId + " | status BEFORE: " + TradeStatus.PENDING);
            System.out.println("Responder (user " + RESPONDER_ID + ") accepts the offer");
            System.out.println("Item A " + itemAId + " status BEFORE: " + ItemStatus.AVAILABLE);
            System.out.println("Item B " + itemBId + " status BEFORE: " + ItemStatus.AVAILABLE);

            tradeService.acceptOffer(offerId, responderJwt);

            System.out.println("--- After Accept ---");
            System.out.println("Offer status AFTER:  " + offer.getStatus());
            System.out.println("Item A status AFTER: " + itemA.getStatus());
            System.out.println("Item B status AFTER: " + itemB.getStatus());
            System.out.println("New expiry (confirmation window): " + offer.getExpiresAt());

            assertEquals(TradeStatus.ACCEPTED, offer.getStatus());
            assertEquals(ItemStatus.IN_TRADE, itemA.getStatus());
            assertEquals(ItemStatus.IN_TRADE, itemB.getStatus());
            assertNotNull(offer.getExpiresAt());
        }

        @Test
        void autoRejectsConflictingOffers() {
            UUID offerId = UUID.randomUUID();
            UUID itemAId = UUID.randomUUID();
            UUID itemBId = UUID.randomUUID();

            Item itemA = buildItem(itemAId, OFFERER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN);
            Item itemB = buildItem(itemBId, RESPONDER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN);
            TradeOffer offer = buildPendingOffer(offerId, itemA, itemB);

            TradeOffer conflicting = TradeOffer.builder()
                    .id(UUID.randomUUID())
                    .status(TradeStatus.PENDING)
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));
            when(itemRepository.findAllByIdForUpdate(any())).thenReturn(List.of(itemA, itemB));
            when(tradeOfferRepository.findAllByItemIdsAndStatus(any(), eq(TradeStatus.PENDING))).thenReturn(List.of(offer, conflicting));
            when(tradeOfferRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            System.out.println("\n=== ACCEPT OFFER - Auto-Reject Conflicting ===");
            System.out.println("Accepting offer " + offerId);
            System.out.println("Conflicting offer " + conflicting.getId() + " | status BEFORE: " + conflicting.getStatus());

            tradeService.acceptOffer(offerId, responderJwt);

            System.out.println("Conflicting offer status AFTER: " + conflicting.getStatus());

            assertEquals(TradeStatus.REJECTED, conflicting.getStatus());
        }

        @Test
        void notPending_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.REJECTED)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== ACCEPT OFFER - Not Pending ===");
            System.out.println("Offer " + offerId + " has status " + offer.getStatus() + ", trying to accept");

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.acceptOffer(offerId, responderJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void callerIsNotResponder_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.PENDING)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== ACCEPT OFFER - Caller Is Not Responder ===");
            System.out.println("Offerer (user " + OFFERER_ID + ") tries to accept their own offer");

            HttpForbiddenError ex = assertThrows(HttpForbiddenError.class, () -> tradeService.acceptOffer(offerId, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void itemNoLongerAvailable_throws() {
            UUID offerId = UUID.randomUUID();
            UUID itemAId = UUID.randomUUID();
            UUID itemBId = UUID.randomUUID();

            Item itemA = buildItem(itemAId, OFFERER_ID, ItemStatus.IN_TRADE, BigDecimal.TEN);
            Item itemB = buildItem(itemBId, RESPONDER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN);
            TradeOffer offer = buildPendingOffer(offerId, itemA, itemB);

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));
            when(itemRepository.findAllByIdForUpdate(any())).thenReturn(List.of(itemA, itemB));

            System.out.println("\n=== ACCEPT OFFER - Item No Longer Available ===");
            System.out.println("Item A " + itemAId + " status: " + itemA.getStatus() + " (already locked by another trade)");

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.acceptOffer(offerId, responderJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void expiredOffer_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.PENDING)
                    .expiresAt(Instant.now().minus(1, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));
            when(tradeOfferRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            System.out.println("\n=== ACCEPT OFFER - Expired ===");
            System.out.println("Offer " + offerId + " expired at " + offer.getExpiresAt());
            System.out.println("Status BEFORE: " + offer.getStatus());

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.acceptOffer(offerId, responderJwt));
            System.out.println("Status AFTER:  " + offer.getStatus());
            System.out.println("BLOCKED: " + ex.getMessage());

            assertEquals(TradeStatus.EXPIRED, offer.getStatus());
        }
    }

    // ==================== rejectOffer ====================

    @Nested
    class RejectOffer {

        @Test
        void happyPath_setsRejected() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.PENDING)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));
            when(tradeOfferRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            System.out.println("\n=== REJECT OFFER - Happy Path ===");
            System.out.println("Offer " + offerId + " | status BEFORE: " + offer.getStatus());
            System.out.println("Responder (user " + RESPONDER_ID + ") rejects");

            tradeService.rejectOffer(offerId, responderJwt);

            System.out.println("Status AFTER: " + offer.getStatus());
            assertEquals(TradeStatus.REJECTED, offer.getStatus());
        }

        @Test
        void notPending_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.ACCEPTED)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== REJECT OFFER - Not Pending ===");
            System.out.println("Offer status: " + offer.getStatus() + ", trying to reject");

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.rejectOffer(offerId, responderJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void callerIsNotResponder_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.PENDING)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== REJECT OFFER - Caller Is Not Responder ===");
            System.out.println("Offerer (user " + OFFERER_ID + ") tries to reject their own offer");

            HttpForbiddenError ex = assertThrows(HttpForbiddenError.class, () -> tradeService.rejectOffer(offerId, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }
    }

    // ==================== withdrawOffer ====================

    @Nested
    class WithdrawOffer {

        @Test
        void happyPath_setsWithdrawn() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.PENDING)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));
            when(tradeOfferRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            System.out.println("\n=== WITHDRAW OFFER - Happy Path ===");
            System.out.println("Offer " + offerId + " | status BEFORE: " + offer.getStatus());
            System.out.println("Offerer (user " + OFFERER_ID + ") withdraws");

            tradeService.withdrawOffer(offerId, offererJwt);

            System.out.println("Status AFTER: " + offer.getStatus());
            assertEquals(TradeStatus.WITHDRAWN, offer.getStatus());
        }

        @Test
        void notPending_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.ACCEPTED)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== WITHDRAW OFFER - Not Pending ===");
            System.out.println("Offer status: " + offer.getStatus() + ", trying to withdraw");

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.withdrawOffer(offerId, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void callerIsNotOfferer_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.PENDING)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== WITHDRAW OFFER - Caller Is Not Offerer ===");
            System.out.println("Responder (user " + RESPONDER_ID + ") tries to withdraw someone else's offer");

            HttpForbiddenError ex = assertThrows(HttpForbiddenError.class, () -> tradeService.withdrawOffer(offerId, responderJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }
    }

    // ==================== counterOffer ====================

    @Nested
    class CounterOffer {

        @Test
        void happyPath_countersOriginalAndCreatesNew() {
            UUID offerId = UUID.randomUUID();
            UUID itemA = UUID.randomUUID();
            UUID itemB = UUID.randomUUID();

            TradeOffer original = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.PENDING)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            TradeOfferCreationDto dto = new TradeOfferCreationDto(OFFERER_ID, List.of(itemB), List.of(itemA));

            Item responderItem = buildItem(itemB, RESPONDER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN);
            Item offererItem = buildItem(itemA, OFFERER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN);

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(original));
            when(itemRepository.findAllById(List.of(itemB))).thenReturn(List.of(responderItem));
            when(itemRepository.findAllById(List.of(itemA))).thenReturn(List.of(offererItem));
            when(tradeOfferRepository.save(any(TradeOffer.class))).thenAnswer(inv -> {
                TradeOffer o = inv.getArgument(0);
                if (o.getId() == null) o.setId(UUID.randomUUID());
                return o;
            });

            System.out.println("\n=== COUNTER OFFER - Happy Path ===");
            System.out.println("Original offer " + offerId + " | status BEFORE: " + original.getStatus());
            System.out.println("Responder (user " + RESPONDER_ID + ") counters with different items");

            TradeOffer counter = tradeService.counterOffer(offerId, dto, responderJwt);

            System.out.println("--- After Counter ---");
            System.out.println("Original offer status AFTER: " + original.getStatus());
            System.out.println("Counter offer ID:     " + counter.getId());
            System.out.println("Counter offer status: " + counter.getStatus());
            System.out.println("Counter offer parent: " + (counter.getParent() != null ? counter.getParent().getId() : "null"));
            System.out.println("Counter offerer:      user " + counter.getOffererId() + " (was responder)");
            System.out.println("Counter responder:    user " + counter.getResponderId() + " (was offerer)");

            assertEquals(TradeStatus.COUNTERED, original.getStatus());
            assertEquals(TradeStatus.PENDING, counter.getStatus());
            assertEquals(original, counter.getParent());
        }

        @Test
        void notPending_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.ACCEPTED)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== COUNTER OFFER - Not Pending ===");
            System.out.println("Offer status: " + offer.getStatus() + ", trying to counter");

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () ->
                    tradeService.counterOffer(offerId, new TradeOfferCreationDto(OFFERER_ID, List.of(UUID.randomUUID()), List.of(UUID.randomUUID())), responderJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void callerIsNotResponder_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.PENDING)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== COUNTER OFFER - Caller Is Not Responder ===");
            System.out.println("Offerer (user " + OFFERER_ID + ") tries to counter their own offer");

            HttpForbiddenError ex = assertThrows(HttpForbiddenError.class, () ->
                    tradeService.counterOffer(offerId, new TradeOfferCreationDto(OFFERER_ID, List.of(UUID.randomUUID()), List.of(UUID.randomUUID())), offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }
    }

    // ==================== cancelOffer ====================

    @Nested
    class CancelOffer {

        @Test
        void happyPath_cancelAndReleasesItems() {
            UUID offerId = UUID.randomUUID();
            Item itemA = buildItem(UUID.randomUUID(), OFFERER_ID, ItemStatus.IN_TRADE, BigDecimal.TEN);
            Item itemB = buildItem(UUID.randomUUID(), RESPONDER_ID, ItemStatus.IN_TRADE, BigDecimal.TEN);

            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.ACCEPTED)
                    .expiresAt(Instant.now().plus(72, ChronoUnit.HOURS))
                    .offerItems(List.of(
                            new OfferItem(itemA, null, OwningSide.OFFERER),
                            new OfferItem(itemB, null, OwningSide.RESPONDER)
                    ))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));
            when(tradeOfferRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            System.out.println("\n=== CANCEL OFFER - Happy Path ===");
            System.out.println("Offer " + offerId + " | status BEFORE: " + offer.getStatus());
            System.out.println("Item A " + itemA.getId() + " status BEFORE: " + itemA.getStatus());
            System.out.println("Item B " + itemB.getId() + " status BEFORE: " + itemB.getStatus());
            System.out.println("Offerer (user " + OFFERER_ID + ") cancels");

            tradeService.cancelOffer(offerId, offererJwt);

            System.out.println("--- After Cancel ---");
            System.out.println("Offer status AFTER:  " + offer.getStatus());
            System.out.println("Item A status AFTER: " + itemA.getStatus() + " (released)");
            System.out.println("Item B status AFTER: " + itemB.getStatus() + " (released)");

            assertEquals(TradeStatus.CANCELED, offer.getStatus());
            assertEquals(ItemStatus.AVAILABLE, itemA.getStatus());
            assertEquals(ItemStatus.AVAILABLE, itemB.getStatus());
        }

        @Test
        void notAccepted_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.PENDING)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== CANCEL OFFER - Not Accepted ===");
            System.out.println("Offer status: " + offer.getStatus() + ", trying to cancel");

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.cancelOffer(offerId, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void callerIsNotParticipant_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.ACCEPTED)
                    .expiresAt(Instant.now().plus(72, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== CANCEL OFFER - Not a Participant ===");
            System.out.println("Stranger (user " + STRANGER_ID + ") tries to cancel");

            HttpForbiddenError ex = assertThrows(HttpForbiddenError.class, () -> tradeService.cancelOffer(offerId, strangerJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }
    }

    // ==================== confirmHandoff ====================

    @Nested
    class ConfirmHandoff {

        @Test
        void offererConfirmsFirst_statusStaysAccepted() {
            UUID offerId = UUID.randomUUID();
            Item itemA = buildItem(UUID.randomUUID(), OFFERER_ID, ItemStatus.IN_TRADE, BigDecimal.TEN);
            TradeOffer offer = buildAcceptedOffer(offerId, itemA);

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));
            when(tradeOfferRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            System.out.println("\n=== CONFIRM HANDOFF - Offerer Confirms First ===");
            System.out.println("Offer " + offerId + " | status: " + offer.getStatus());
            System.out.println("Offerer (user " + OFFERER_ID + ") confirms handoff");

            tradeService.confirmHandoff(offerId, offererJwt);

            System.out.println("--- After Offerer Confirms ---");
            System.out.println("Offer status:          " + offer.getStatus() + " (still accepted, waiting for responder)");
            System.out.println("Offerer confirmed at:  " + offer.getOffererConfirmedAt());
            System.out.println("Responder confirmed at: " + offer.getResponderConfirmedAt());

            assertEquals(TradeStatus.ACCEPTED, offer.getStatus());
            assertNotNull(offer.getOffererConfirmedAt());
            assertNull(offer.getResponderConfirmedAt());
        }

        @Test
        void bothConfirm_completesTradeAndSetsItemsTraded() {
            UUID offerId = UUID.randomUUID();
            Item itemA = buildItem(UUID.randomUUID(), OFFERER_ID, ItemStatus.IN_TRADE, BigDecimal.TEN);
            Item itemB = buildItem(UUID.randomUUID(), RESPONDER_ID, ItemStatus.IN_TRADE, BigDecimal.TEN);

            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.ACCEPTED)
                    .expiresAt(Instant.now().plus(72, ChronoUnit.HOURS))
                    .offererConfirmedAt(LocalDateTime.now())
                    .offerItems(List.of(
                            new OfferItem(itemA, null, OwningSide.OFFERER),
                            new OfferItem(itemB, null, OwningSide.RESPONDER)
                    ))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));
            when(tradeOfferRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            System.out.println("\n=== CONFIRM HANDOFF - Both Confirm (Trade Completes) ===");
            System.out.println("Offer " + offerId + " | status: " + offer.getStatus());
            System.out.println("Offerer already confirmed at: " + offer.getOffererConfirmedAt());
            System.out.println("Responder (user " + RESPONDER_ID + ") now confirms");
            System.out.println("Item A " + itemA.getId() + " status BEFORE: " + itemA.getStatus());
            System.out.println("Item B " + itemB.getId() + " status BEFORE: " + itemB.getStatus());

            tradeService.confirmHandoff(offerId, responderJwt);

            System.out.println("--- After Both Confirm ---");
            System.out.println("Offer status AFTER:  " + offer.getStatus());
            System.out.println("Item A status AFTER: " + itemA.getStatus());
            System.out.println("Item B status AFTER: " + itemB.getStatus());
            System.out.println("TRADE COMPLETED SUCCESSFULLY");

            assertEquals(TradeStatus.COMPLETED, offer.getStatus());
            assertEquals(ItemStatus.TRADED, itemA.getStatus());
            assertEquals(ItemStatus.TRADED, itemB.getStatus());
        }

        @Test
        void notAccepted_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.PENDING)
                    .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== CONFIRM HANDOFF - Not Accepted ===");
            System.out.println("Offer status: " + offer.getStatus() + ", trying to confirm");

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.confirmHandoff(offerId, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void alreadyConfirmed_throws() {
            UUID offerId = UUID.randomUUID();
            Item itemA = buildItem(UUID.randomUUID(), OFFERER_ID, ItemStatus.IN_TRADE, BigDecimal.TEN);

            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.ACCEPTED)
                    .expiresAt(Instant.now().plus(72, ChronoUnit.HOURS))
                    .offererConfirmedAt(LocalDateTime.now())
                    .offerItems(List.of(new OfferItem(itemA, null, OwningSide.OFFERER)))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== CONFIRM HANDOFF - Already Confirmed ===");
            System.out.println("Offerer already confirmed at " + offer.getOffererConfirmedAt() + ", tries to confirm again");

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.confirmHandoff(offerId, offererJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }

        @Test
        void notAParticipant_throws() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.ACCEPTED)
                    .expiresAt(Instant.now().plus(72, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));

            System.out.println("\n=== CONFIRM HANDOFF - Not a Participant ===");
            System.out.println("Stranger (user " + STRANGER_ID + ") tries to confirm");

            HttpForbiddenError ex = assertThrows(HttpForbiddenError.class, () -> tradeService.confirmHandoff(offerId, strangerJwt));
            System.out.println("BLOCKED: " + ex.getMessage());
        }
    }

    // ==================== checkExpiry (tested indirectly) ====================

    @Nested
    class ExpiryCheck {

        @Test
        void expiredPendingOffer_transitionsToExpired() {
            UUID offerId = UUID.randomUUID();
            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.PENDING)
                    .expiresAt(Instant.now().minus(1, ChronoUnit.HOURS))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));
            when(tradeOfferRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            System.out.println("\n=== EXPIRY CHECK - Expired PENDING Offer ===");
            System.out.println("Offer " + offerId + " | status: " + offer.getStatus() + " | expired at: " + offer.getExpiresAt());
            System.out.println("Responder tries to reject, but lazy expiry check fires first");

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.rejectOffer(offerId, responderJwt));
            System.out.println("Status AFTER: " + offer.getStatus());
            System.out.println("BLOCKED: " + ex.getMessage());

            assertEquals(TradeStatus.EXPIRED, offer.getStatus());
        }

        @Test
        void expiredAcceptedOffer_releasesItemsAndExpires() {
            UUID offerId = UUID.randomUUID();
            Item itemA = buildItem(UUID.randomUUID(), OFFERER_ID, ItemStatus.IN_TRADE, BigDecimal.TEN);
            Item itemB = buildItem(UUID.randomUUID(), RESPONDER_ID, ItemStatus.IN_TRADE, BigDecimal.TEN);

            TradeOffer offer = TradeOffer.builder()
                    .id(offerId)
                    .offererId(OFFERER_ID)
                    .responderId(RESPONDER_ID)
                    .status(TradeStatus.ACCEPTED)
                    .expiresAt(Instant.now().minus(1, ChronoUnit.HOURS))
                    .offerItems(List.of(
                            new OfferItem(itemA, null, OwningSide.OFFERER),
                            new OfferItem(itemB, null, OwningSide.RESPONDER)
                    ))
                    .build();

            when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.of(offer));
            when(tradeOfferRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            System.out.println("\n=== EXPIRY CHECK - Expired ACCEPTED Offer (items released) ===");
            System.out.println("Offer " + offerId + " | status: " + offer.getStatus() + " | expired at: " + offer.getExpiresAt());
            System.out.println("Item A " + itemA.getId() + " status BEFORE: " + itemA.getStatus());
            System.out.println("Item B " + itemB.getId() + " status BEFORE: " + itemB.getStatus());
            System.out.println("Offerer tries to confirm, but lazy expiry check fires first");

            HttpBadRequestException ex = assertThrows(HttpBadRequestException.class, () -> tradeService.confirmHandoff(offerId, offererJwt));
            System.out.println("--- After Expiry ---");
            System.out.println("Offer status AFTER:  " + offer.getStatus());
            System.out.println("Item A status AFTER: " + itemA.getStatus() + " (released)");
            System.out.println("Item B status AFTER: " + itemB.getStatus() + " (released)");
            System.out.println("BLOCKED: " + ex.getMessage());

            assertEquals(TradeStatus.EXPIRED, offer.getStatus());
            assertEquals(ItemStatus.AVAILABLE, itemA.getStatus());
            assertEquals(ItemStatus.AVAILABLE, itemB.getStatus());
        }
    }

    // ==================== offerNotFound ====================

    @Test
    void anyAction_offerNotFound_throws() {
        UUID offerId = UUID.randomUUID();
        when(tradeOfferRepository.findById(offerId)).thenReturn(Optional.empty());

        System.out.println("\n=== OFFER NOT FOUND ===");
        System.out.println("Trying to accept non-existent offer " + offerId);

        HttpNotFoundException ex = assertThrows(HttpNotFoundException.class, () -> tradeService.acceptOffer(offerId, responderJwt));
        System.out.println("BLOCKED: " + ex.getMessage());
    }

    // ==================== Helpers ====================

    private Jwt buildJwt() {
        return new Jwt(
                "token-value",
                Instant.now(),
                Instant.now().plusSeconds(300),
                Map.of("alg", "RS256"),
                Map.of("sub", UUID.randomUUID().toString())
        );
    }

    private User buildUser(Long id) {
        return User.builder().id(id).build();
    }

    private Item buildItem(UUID id, Long ownerId, ItemStatus status, BigDecimal value) {
        return Item.builder()
                .id(id)
                .ownerId(ownerId)
                .status(status)
                .estimatedValue(value)
                .build();
    }

    private TradeOffer buildPendingOffer(UUID offerId, Item offererItem, Item responderItem) {
        TradeOffer offer = TradeOffer.builder()
                .id(offerId)
                .offererId(OFFERER_ID)
                .responderId(RESPONDER_ID)
                .status(TradeStatus.PENDING)
                .expiresAt(Instant.now().plus(48, ChronoUnit.HOURS))
                .build();

        offer.setOfferItems(List.of(
                new OfferItem(offererItem, offer, OwningSide.OFFERER),
                new OfferItem(responderItem, offer, OwningSide.RESPONDER)
        ));
        return offer;
    }

    private TradeOffer buildAcceptedOffer(UUID offerId, Item... items) {
        List<OfferItem> offerItems = Arrays.stream(items)
                .map(item -> new OfferItem(item, null, OwningSide.OFFERER))
                .toList();

        return TradeOffer.builder()
                .id(offerId)
                .offererId(OFFERER_ID)
                .responderId(RESPONDER_ID)
                .status(TradeStatus.ACCEPTED)
                .expiresAt(Instant.now().plus(72, ChronoUnit.HOURS))
                .offerItems(offerItems)
                .build();
    }
}
