package com.tskhra.modulith.trade_module.services;

import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.domain.OfferItem;
import com.tskhra.modulith.trade_module.model.domain.TradeOffer;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.enums.TradeStatus;
import com.tskhra.modulith.trade_module.elastic.services.ItemSearchService;
import com.tskhra.modulith.trade_module.repositories.ItemRepository;
import com.tskhra.modulith.trade_module.repositories.TradeOfferRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;

@Slf4j
@Component
@RequiredArgsConstructor
public class TradeOfferExpiryJob {

    private final TradeOfferRepository tradeOfferRepository;
    private final ItemRepository itemRepository;
    private final ItemSearchService itemSearchService;

    @Scheduled(fixedRate = 30 * 60 * 1000)
    @Transactional
    public void expireOffers() {
        List<TradeOffer> expired = tradeOfferRepository.findExpiredOffers(
                List.of(TradeStatus.PENDING, TradeStatus.ACCEPTED), Instant.now());

        if (expired.isEmpty()) return;

        int pendingCount = 0;
        int acceptedCount = 0;

        for (TradeOffer offer : expired) {
            if (offer.getStatus() == TradeStatus.ACCEPTED) {
                releaseItems(offer);
                acceptedCount++;
            } else {
                pendingCount++;
            }
            offer.setStatus(TradeStatus.EXPIRED);
        }

        tradeOfferRepository.saveAll(expired);
        log.info("Expired {} trade offers ({} PENDING, {} ACCEPTED with items released)",
                expired.size(), pendingCount, acceptedCount);
    }

    private void releaseItems(TradeOffer offer) {
        List<Item> items = offer.getOfferItems().stream()
                .map(OfferItem::getItem)
                .toList();
        items.forEach(item -> {
            item.setStatus(ItemStatus.AVAILABLE);
            itemSearchService.updateItemStatus(item.getId(), ItemStatus.AVAILABLE);
        });
        itemRepository.saveAll(items);
    }
}