package com.tskhra.modulith.trade_module.model.events;

import com.tskhra.modulith.trade_module.model.enums.ItemStatus;

import java.util.UUID;

public record ItemStatusChangedEvent(UUID itemId, ItemStatus oldStatus, ItemStatus newStatus) {
}
