package com.tskhra.modulith.trade_module.repositories;

import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import jakarta.persistence.LockModeType;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface ItemRepository extends JpaRepository<Item, UUID> {

    Page<Item> findAllByStatus(ItemStatus status, Pageable pageable);

    Page<Item> findAllByOwnerIdAndStatus(Long ownerId, ItemStatus status, Pageable pageable);

    Page<Item> findAllByOwnerId(Long ownerId, Pageable pageable);

    @Query("SELECT i FROM Item i WHERE i.ownerId = :userId AND i.status IN :statuses")
    Page<Item> findAllByOwnerIdAndStatuses(@Param("userId") Long userId, @Param("statuses") List<ItemStatus> statuses, Pageable pageable);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT i FROM Item i WHERE i.id IN :ids")
    List<Item> findAllByIdForUpdate(@Param("ids") List<UUID> ids);
}