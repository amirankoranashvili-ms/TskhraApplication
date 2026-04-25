package com.tskhra.modulith.trade_module.model.domain;

import java.io.Serializable;
import java.util.Objects;
import java.util.UUID;

public class ItemDesiredTypeId implements Serializable {

    private UUID item;
    private Integer itemType;

    public ItemDesiredTypeId() {}

    public ItemDesiredTypeId(UUID item, Integer itemType) {
        this.item = item;
        this.itemType = itemType;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof ItemDesiredTypeId that)) return false;
        return Objects.equals(item, that.item) && Objects.equals(itemType, that.itemType);
    }

    @Override
    public int hashCode() {
        return Objects.hash(item, itemType);
    }

}
