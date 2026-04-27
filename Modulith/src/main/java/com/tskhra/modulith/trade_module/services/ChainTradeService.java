package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpForbiddenError;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.trade_module.elastic.services.ItemSearchService;
import com.tskhra.modulith.trade_module.graph.services.TradeGraphService;
import com.tskhra.modulith.trade_module.model.domain.ChainLink;
import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.domain.TradeChain;
import com.tskhra.modulith.trade_module.model.enums.ChainStatus;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.events.ItemStatusChangedEvent;
import com.tskhra.modulith.trade_module.model.requests.ChainProposalDto;
import com.tskhra.modulith.trade_module.model.responses.ChainCandidateDto;
import com.tskhra.modulith.trade_module.model.responses.ChainTradeSummaryDto;
import com.tskhra.modulith.trade_module.repositories.ItemRepository;
import com.tskhra.modulith.trade_module.repositories.TradeChainRepository;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

@Service
@RequiredArgsConstructor
public class ChainTradeService {

    private static final long PROPOSAL_EXPIRY_HOURS = 48;
    private static final long ACTIVE_EXPIRY_HOURS = 72;

    private final TradeGraphService graphService;
    private final TradeChainRepository chainRepository;
    private final ItemRepository itemRepository;
    private final UserService userService;
    private final ItemSearchService itemSearchService;
    private final ApplicationEventPublisher eventPublisher;

    @Transactional(readOnly = true)
    public List<ChainCandidateDto> discoverChains(UUID itemId, int maxResults, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();

        Item item = itemRepository.findById(itemId)
                .orElseThrow(() -> new HttpNotFoundException("Item not found"));

        if (!item.getOwnerId().equals(userId)) {
            throw new HttpForbiddenError("You can only discover chains for your own items");
        }

        if (item.getStatus() != ItemStatus.AVAILABLE) {
            throw new HttpBadRequestException("Item must be AVAILABLE to discover chains");
        }

        List<Map<String, Object>> rawChains = graphService.findChains(itemId, maxResults);
        return rawChains.stream()
                .map(this::toChainCandidate)
                .filter(Objects::nonNull)
                .toList();
    }

    @Transactional
    public ChainTradeSummaryDto proposeChain(ChainProposalDto dto, Jwt jwt) {
        Long initiatorId = userService.getCurrentUser(jwt).getId();

        List<Item> items = new ArrayList<>();
        for (UUID itemId : dto.itemIds()) {
            Item item = itemRepository.findById(itemId)
                    .orElseThrow(() -> new HttpNotFoundException("Item not found: " + itemId));
            if (item.getStatus() != ItemStatus.AVAILABLE) {
                throw new HttpBadRequestException("Item " + item.getName() + " is not available");
            }
            items.add(item);
        }

        boolean initiatorOwnsFirst = items.getFirst().getOwnerId().equals(initiatorId);
        boolean initiatorInChain = items.stream().anyMatch(i -> i.getOwnerId().equals(initiatorId));
        if (!initiatorInChain) {
            throw new HttpForbiddenError("You must be a participant in the chain");
        }

        Set<Long> ownerIds = new HashSet<>();
        for (Item item : items) {
            if (!ownerIds.add(item.getOwnerId())) {
                throw new HttpBadRequestException("Each participant must appear exactly once in the chain");
            }
        }

        TradeChain chain = TradeChain.builder()
                .status(ChainStatus.PROPOSED)
                .initiatorId(initiatorId)
                .expiresAt(Instant.now().plus(PROPOSAL_EXPIRY_HOURS, ChronoUnit.HOURS))
                .build();

        List<ChainLink> links = new ArrayList<>();
        for (int i = 0; i < items.size(); i++) {
            Item giver = items.get(i);
            Item receiver = items.get((i + items.size() - 1) % items.size());

            ChainLink link = ChainLink.builder()
                    .chain(chain)
                    .position(i)
                    .giverId(giver.getOwnerId())
                    .item(giver)
                    .receiverId(receiver.getOwnerId())
                    .build();

            if (giver.getOwnerId().equals(initiatorId)) {
                link.setAcceptedAt(LocalDateTime.now());
            }

            links.add(link);
        }
        chain.setLinks(links);

        TradeChain saved = chainRepository.save(chain);
        return toSummaryDto(saved);
    }

    @Transactional
    public void acceptChain(UUID chainId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        TradeChain chain = getChainOrThrow(chainId);
        checkChainExpiry(chain);

        if (chain.getStatus() != ChainStatus.PROPOSED) {
            throw new HttpBadRequestException("Only PROPOSED chains can be accepted");
        }

        ChainLink myLink = findUserLink(chain, userId);
        if (myLink.getAcceptedAt() != null) {
            throw new HttpBadRequestException("You have already accepted this chain");
        }

        myLink.setAcceptedAt(LocalDateTime.now());

        boolean allAccepted = chain.getLinks().stream()
                .allMatch(l -> l.getAcceptedAt() != null);

        if (allAccepted) {
            List<UUID> itemIds = chain.getLinks().stream()
                    .map(l -> l.getItem().getId())
                    .toList();
            List<Item> lockedItems = itemRepository.findAllByIdForUpdate(itemIds);

            boolean allAvailable = lockedItems.stream()
                    .allMatch(item -> item.getStatus() == ItemStatus.AVAILABLE);
            if (!allAvailable) {
                chain.setStatus(ChainStatus.BROKEN);
                chainRepository.save(chain);
                throw new HttpBadRequestException("One or more items are no longer available — chain broken");
            }

            lockedItems.forEach(item -> {
                ItemStatus oldStatus = item.getStatus();
                item.setStatus(ItemStatus.IN_TRADE);
                itemSearchService.updateItemStatus(item.getId(), ItemStatus.IN_TRADE);
                eventPublisher.publishEvent(new ItemStatusChangedEvent(item.getId(), oldStatus, ItemStatus.IN_TRADE));
            });
            itemRepository.saveAll(lockedItems);

            chain.setStatus(ChainStatus.ACTIVE);
            chain.setExpiresAt(Instant.now().plus(ACTIVE_EXPIRY_HOURS, ChronoUnit.HOURS));
        }

        chainRepository.save(chain);
    }

    @Transactional
    public void rejectChain(UUID chainId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        TradeChain chain = getChainOrThrow(chainId);

        if (chain.getStatus() != ChainStatus.PROPOSED && chain.getStatus() != ChainStatus.ACTIVE) {
            throw new HttpBadRequestException("Cannot reject a chain in " + chain.getStatus() + " status");
        }

        findUserLink(chain, userId);

        if (chain.getStatus() == ChainStatus.ACTIVE) {
            releaseChainItems(chain);
        }

        chain.setStatus(ChainStatus.BROKEN);
        chainRepository.save(chain);
    }

    @Transactional
    public void confirmHandoff(UUID chainId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        TradeChain chain = getChainOrThrow(chainId);
        checkChainExpiry(chain);

        if (chain.getStatus() != ChainStatus.ACTIVE) {
            throw new HttpBadRequestException("Only ACTIVE chains can be confirmed");
        }

        ChainLink myLink = findUserLink(chain, userId);
        if (myLink.getConfirmedAt() != null) {
            throw new HttpBadRequestException("You have already confirmed handoff");
        }

        myLink.setConfirmedAt(LocalDateTime.now());

        boolean allConfirmed = chain.getLinks().stream()
                .allMatch(l -> l.getConfirmedAt() != null);

        if (allConfirmed) {
            chain.setStatus(ChainStatus.COMPLETED);
            chain.getLinks().forEach(link -> {
                Item item = link.getItem();
                item.setStatus(ItemStatus.TRADED);
                itemSearchService.updateItemStatus(item.getId(), ItemStatus.TRADED);
                eventPublisher.publishEvent(new ItemStatusChangedEvent(item.getId(), ItemStatus.IN_TRADE, ItemStatus.TRADED));
            });
        }

        chainRepository.save(chain);
    }

    @Transactional(readOnly = true)
    public ChainTradeSummaryDto getChainDetails(UUID chainId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();
        TradeChain chain = getChainOrThrow(chainId);
        findUserLink(chain, userId);
        return toSummaryDto(chain);
    }

    @Transactional(readOnly = true)
    public Page<ChainTradeSummaryDto> getMyChainTrades(Jwt jwt, ChainStatus status, Pageable pageable) {
        Long userId = userService.getCurrentUser(jwt).getId();
        Page<TradeChain> chains = status != null
                ? chainRepository.findAllByParticipantAndStatus(userId, status, pageable)
                : chainRepository.findAllByParticipant(userId, pageable);
        return chains.map(this::toSummaryDto);
    }

    private TradeChain getChainOrThrow(UUID chainId) {
        return chainRepository.findById(chainId)
                .orElseThrow(() -> new HttpNotFoundException("Chain trade not found"));
    }

    private ChainLink findUserLink(TradeChain chain, Long userId) {
        return chain.getLinks().stream()
                .filter(l -> l.getGiverId().equals(userId))
                .findFirst()
                .orElseThrow(() -> new HttpForbiddenError("You are not a participant in this chain"));
    }

    private void checkChainExpiry(TradeChain chain) {
        if (chain.getExpiresAt() != null && Instant.now().isAfter(chain.getExpiresAt())
                && (chain.getStatus() == ChainStatus.PROPOSED || chain.getStatus() == ChainStatus.ACTIVE)) {
            if (chain.getStatus() == ChainStatus.ACTIVE) {
                releaseChainItems(chain);
            }
            chain.setStatus(ChainStatus.EXPIRED);
            chainRepository.save(chain);
            throw new HttpBadRequestException("This chain trade has expired");
        }
    }

    private void releaseChainItems(TradeChain chain) {
        chain.getLinks().forEach(link -> {
            Item item = link.getItem();
            ItemStatus oldStatus = item.getStatus();
            item.setStatus(ItemStatus.AVAILABLE);
            itemSearchService.updateItemStatus(item.getId(), ItemStatus.AVAILABLE);
            eventPublisher.publishEvent(new ItemStatusChangedEvent(item.getId(), oldStatus, ItemStatus.AVAILABLE));
        });
    }

    @SuppressWarnings("unchecked")
    private ChainCandidateDto toChainCandidate(Map<String, Object> raw) {
        Object chainObj = raw.get("chain");
        if (!(chainObj instanceof List<?> chainList)) return null;

        List<ChainCandidateDto.ChainLinkDto> links = new ArrayList<>();
        for (int i = 0; i < chainList.size(); i++) {
            Map<String, Object> node = (Map<String, Object>) chainList.get(i);
            links.add(new ChainCandidateDto.ChainLinkDto(
                    i,
                    UUID.fromString((String) node.get("itemId")),
                    (String) node.get("name"),
                    ((Number) node.get("ownerId")).longValue(),
                    (String) node.get("categoryName"),
                    node.get("estimatedValue") != null
                            ? new BigDecimal(node.get("estimatedValue").toString())
                            : null
            ));
        }

        return new ChainCandidateDto(links, links.size());
    }

    private ChainTradeSummaryDto toSummaryDto(TradeChain chain) {
        List<ChainTradeSummaryDto.ChainLinkSummaryDto> links = chain.getLinks().stream()
                .map(l -> new ChainTradeSummaryDto.ChainLinkSummaryDto(
                        l.getPosition(),
                        l.getGiverId(),
                        l.getItem().getId(),
                        l.getItem().getName(),
                        l.getReceiverId(),
                        l.getAcceptedAt() != null,
                        l.getConfirmedAt() != null
                ))
                .toList();

        return new ChainTradeSummaryDto(
                chain.getId(),
                chain.getStatus(),
                chain.getInitiatorId(),
                links,
                chain.getExpiresAt(),
                chain.getCreatedAt()
        );
    }

}
