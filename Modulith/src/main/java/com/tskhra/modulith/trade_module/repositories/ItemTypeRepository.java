package com.tskhra.modulith.trade_module.repositories;

import com.tskhra.modulith.trade_module.model.domain.ItemType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ItemTypeRepository extends JpaRepository<ItemType, Integer> {

    Optional<ItemType> findBySlug(String slug);

    boolean existsBySlug(String slug);

    List<ItemType> findAllByCategoryId(Integer categoryId);

}
