package com.tskhra.modulith.trade_module.repositories;

import com.tskhra.modulith.trade_module.model.domain.ItemTypeAttribute;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ItemTypeAttributeRepository extends JpaRepository<ItemTypeAttribute, Integer> {

    List<ItemTypeAttribute> findAllByItemTypeId(Integer itemTypeId);

    Optional<ItemTypeAttribute> findByItemTypeIdAndAttributeId(Integer itemTypeId, Integer attributeId);

    boolean existsByItemTypeIdAndAttributeId(Integer itemTypeId, Integer attributeId);

}
