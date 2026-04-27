package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.trade_module.elastic.services.ItemSearchService;
import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.domain.TradeChain;
import com.tskhra.modulith.trade_module.model.enums.ChainStatus;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.events.ItemStatusChangedEvent;
import com.tskhra.modulith.trade_module.repositories.TradeChainRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;

@Component
@RequiredArgsConstructor
@Slf4j
public class ChainExpiryJob {

    private final TradeChainRepository chainRepository;
    private final ItemSearchService itemSearchService;
    private final ApplicationEventPublisher eventPublisher;

    @Scheduled(fixedRate = 1800000)
    @Transactional
    public void expireChains() {
        Instant now = Instant.now();

        List<TradeChain> expiredProposed = chainRepository
                .findAllByStatusAndExpiresAtBefore(ChainStatus.PROPOSED, now);
        for (TradeChain chain : expiredProposed) {
            chain.setStatus(ChainStatus.EXPIRED);
            log.info("Expired PROPOSED chain {}", chain.getId());
        }
        chainRepository.saveAll(expiredProposed);

        List<TradeChain> expiredActive = chainRepository
                .findAllByStatusAndExpiresAtBefore(ChainStatus.ACTIVE, now);
        for (TradeChain chain : expiredActive) {
            chain.getLinks().forEach(link -> {
                Item item = link.getItem();
                ItemStatus oldStatus = item.getStatus();
                item.setStatus(ItemStatus.AVAILABLE);
                itemSearchService.updateItemStatus(item.getId(), ItemStatus.AVAILABLE);
                eventPublisher.publishEvent(new ItemStatusChangedEvent(item.getId(), oldStatus, ItemStatus.AVAILABLE));
            });
            chain.setStatus(ChainStatus.EXPIRED);
            log.info("Expired ACTIVE chain {}, released items", chain.getId());
        }
        chainRepository.saveAll(expiredActive);
    }

}
