package com.tskhra.modulith.trade_module.repositories;

import com.tskhra.modulith.trade_module.model.domain.ItemImage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface ItemImageRepository extends JpaRepository<ItemImage, Long> {

    Optional<ItemImage> findFirstByItemIdOrderByIsMainDesc(UUID itemId);

}