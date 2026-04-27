package com.tskhra.modulith.trade_module.graph.listeners;

import com.tskhra.modulith.trade_module.graph.services.TradeGraphService;
import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.events.ItemCreatedEvent;
import com.tskhra.modulith.trade_module.model.events.ItemStatusChangedEvent;
import com.tskhra.modulith.trade_module.repositories.ItemRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class TradeGraphListener {

    private final TradeGraphService graphService;
    private final ItemRepository itemRepository;

    @EventListener
    @Async
    public void onItemCreated(ItemCreatedEvent event) {
        try {
            Item item = itemRepository.findById(event.itemId()).orElse(null);
            if (item == null || item.getStatus() != ItemStatus.AVAILABLE) return;
            graphService.syncItem(item);
            graphService.computeEdges(item);
            log.debug("Synced new item {} to trade graph", event.itemId());
        } catch (Exception e) {
            log.error("Failed to sync item {} to trade graph", event.itemId(), e);
        }
    }

    @EventListener
    @Async
    public void onItemStatusChanged(ItemStatusChangedEvent event) {
        try {
            if (event.newStatus() == ItemStatus.AVAILABLE) {
                Item item = itemRepository.findById(event.itemId()).orElse(null);
                if (item == null) return;
                graphService.syncItem(item);
                graphService.computeEdges(item);
            } else {
                graphService.removeEdgesForItem(event.itemId());
                graphService.updateNodeStatus(event.itemId(), event.newStatus());
            }
            log.debug("Updated item {} status in trade graph: {} -> {}",
                    event.itemId(), event.oldStatus(), event.newStatus());
        } catch (Exception e) {
            log.error("Failed to update item {} in trade graph", event.itemId(), e);
        }
    }

}
