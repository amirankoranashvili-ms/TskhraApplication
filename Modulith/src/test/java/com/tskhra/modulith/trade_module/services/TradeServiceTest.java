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

            TradeOffer result = tradeService.createOffer(dto, offererJwt);

            assertEquals(TradeStatus.PENDING, result.getStatus());
            assertEquals(OFFERER_ID, result.getOffererId());
            assertEquals(RESPONDER_ID, result.getResponderId());
            assertNotNull(result.getExpiresAt());
            assertNotNull(result.getFairnessRatio());
            assertEquals(2, result.getOfferItems().size());
        }

        @Test
        void sameUserAsOffererAndResponder_throws() {
            TradeOfferCreationDto dto = new TradeOfferCreationDto(OFFERER_ID, List.of(UUID.randomUUID()), List.of(UUID.randomUUID()));

            assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
        }

        @Test
        void duplicateItemIds_throws() {
            UUID sharedId = UUID.randomUUID();
            TradeOfferCreationDto dto = new TradeOfferCreationDto(RESPONDER_ID, List.of(sharedId), List.of(sharedId));

            assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
        }

        @Test
        void offererItemNotFound_throws() {
            UUID itemA = UUID.randomUUID();
            UUID itemB = UUID.randomUUID();
            TradeOfferCreationDto dto = new TradeOfferCreationDto(RESPONDER_ID, List.of(itemA), List.of(itemB));

            when(itemRepository.findAllById(List.of(itemA))).thenReturn(Collections.emptyList());

            assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
        }

        @Test
        void responderItemNotFound_throws() {
            UUID itemA = UUID.randomUUID();
            UUID itemB = UUID.randomUUID();
            TradeOfferCreationDto dto = new TradeOfferCreationDto(RESPONDER_ID, List.of(itemA), List.of(itemB));

            when(itemRepository.findAllById(List.of(itemA))).thenReturn(List.of(buildItem(itemA, OFFERER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN)));
            when(itemRepository.findAllById(List.of(itemB))).thenReturn(Collections.emptyList());

            assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
        }

        @Test
        void offererItemBelongsToWrongUser_throws() {
            UUID itemA = UUID.randomUUID();
            UUID itemB = UUID.randomUUID();
            TradeOfferCreationDto dto = new TradeOfferCreationDto(RESPONDER_ID, List.of(itemA), List.of(itemB));

            when(itemRepository.findAllById(List.of(itemA))).thenReturn(List.of(buildItem(itemA, STRANGER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN)));
            when(itemRepository.findAllById(List.of(itemB))).thenReturn(List.of(buildItem(itemB, RESPONDER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN)));

            assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
        }

        @Test
        void itemNotAvailable_throws() {
            UUID itemA = UUID.randomUUID();
            UUID itemB = UUID.randomUUID();
            TradeOfferCreationDto dto = new TradeOfferCreationDto(RESPONDER_ID, List.of(itemA), List.of(itemB));

            when(itemRepository.findAllById(List.of(itemA))).thenReturn(List.of(buildItem(itemA, OFFERER_ID, ItemStatus.IN_TRADE, BigDecimal.TEN)));
            when(itemRepository.findAllById(List.of(itemB))).thenReturn(List.of(buildItem(itemB, RESPONDER_ID, ItemStatus.AVAILABLE, BigDecimal.TEN)));

            assertThrows(HttpBadRequestException.class, () -> tradeService.createOffer(dto, offererJwt));
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

            tradeService.acceptOffer(offerId, responderJwt);

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

            tradeService.acceptOffer(offerId, responderJwt);

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

            assertThrows(HttpBadRequestException.class, () -> tradeService.acceptOffer(offerId, responderJwt));
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

            assertThrows(HttpForbiddenError.class, () -> tradeService.acceptOffer(offerId, offererJwt));
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

            assertThrows(HttpBadRequestException.class, () -> tradeService.acceptOffer(offerId, responderJwt));
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

            assertThrows(HttpBadRequestException.class, () -> tradeService.acceptOffer(offerId, responderJwt));
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

            tradeService.rejectOffer(offerId, responderJwt);

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

            assertThrows(HttpBadRequestException.class, () -> tradeService.rejectOffer(offerId, responderJwt));
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

            assertThrows(HttpForbiddenError.class, () -> tradeService.rejectOffer(offerId, offererJwt));
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

            tradeService.withdrawOffer(offerId, offererJwt);

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

            assertThrows(HttpBadRequestException.class, () -> tradeService.withdrawOffer(offerId, offererJwt));
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

            assertThrows(HttpForbiddenError.class, () -> tradeService.withdrawOffer(offerId, responderJwt));
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

            // Counter-offer: responder becomes offerer, original offerer becomes responder
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

            TradeOffer counter = tradeService.counterOffer(offerId, dto, responderJwt);

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

            assertThrows(HttpBadRequestException.class, () ->
                    tradeService.counterOffer(offerId, new TradeOfferCreationDto(OFFERER_ID, List.of(UUID.randomUUID()), List.of(UUID.randomUUID())), responderJwt));
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

            assertThrows(HttpForbiddenError.class, () ->
                    tradeService.counterOffer(offerId, new TradeOfferCreationDto(OFFERER_ID, List.of(UUID.randomUUID()), List.of(UUID.randomUUID())), offererJwt));
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

            tradeService.cancelOffer(offerId, offererJwt);

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

            assertThrows(HttpBadRequestException.class, () -> tradeService.cancelOffer(offerId, offererJwt));
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

            assertThrows(HttpForbiddenError.class, () -> tradeService.cancelOffer(offerId, strangerJwt));
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

            tradeService.confirmHandoff(offerId, offererJwt);

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

            tradeService.confirmHandoff(offerId, responderJwt);

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

            assertThrows(HttpBadRequestException.class, () -> tradeService.confirmHandoff(offerId, offererJwt));
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

            assertThrows(HttpBadRequestException.class, () -> tradeService.confirmHandoff(offerId, offererJwt));
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

            assertThrows(HttpForbiddenError.class, () -> tradeService.confirmHandoff(offerId, strangerJwt));
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

            assertThrows(HttpBadRequestException.class, () -> tradeService.rejectOffer(offerId, responderJwt));
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

            assertThrows(HttpBadRequestException.class, () -> tradeService.confirmHandoff(offerId, offererJwt));
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

        assertThrows(HttpNotFoundException.class, () -> tradeService.acceptOffer(offerId, responderJwt));
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
