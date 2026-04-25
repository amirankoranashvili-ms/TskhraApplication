package com.tskhra.modulith.trade_module.repositories;

import com.tskhra.modulith.trade_module.model.domain.ItemDesiredType;
import com.tskhra.modulith.trade_module.model.domain.ItemDesiredTypeId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface ItemDesiredTypeRepository extends JpaRepository<ItemDesiredType, ItemDesiredTypeId> {

    List<ItemDesiredType> findAllByItemId(UUID itemId);

    void deleteAllByItemId(UUID itemId);

}
