package com.tskhra.modulith.trade_module.repositories;

import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface ItemRepository extends JpaRepository<Item, UUID> {

    Page<Item> findAllByStatus(ItemStatus status, Pageable pageable);

    Page<Item> findAllByOwnerIdAndStatus(Long ownerId, ItemStatus status, Pageable pageable);

    Page<Item> findAllByOwnerId(Long ownerId, Pageable pageable);
}