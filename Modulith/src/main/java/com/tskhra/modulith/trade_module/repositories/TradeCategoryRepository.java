package com.tskhra.modulith.trade_module.repositories;

import com.tskhra.modulith.trade_module.model.domain.TradeCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.Optional;

@Repository
public interface TradeCategoryRepository extends JpaRepository<TradeCategory, Integer> {

    Optional<TradeCategory> findBySlug(String slug);

    boolean existsBySlug(String slug);

    @Query("SELECT tc FROM TradeCategory tc WHERE tc.parent IS NULL")
    List<TradeCategory> findAllParents();

    @Query("SELECT DISTINCT tc FROM TradeCategory tc LEFT JOIN FETCH tc.children WHERE tc.parent IS NULL")
    List<TradeCategory> findAllParentsWithChildren();

    Page<TradeCategory> findAllByParentIsNull(Pageable pageable);

    @Query("SELECT COUNT(tc) > 0 FROM TradeCategory tc WHERE tc.parent.id = :categoryId")
    boolean isParentCategoryById(@Param("categoryId") Integer categoryId);

    @Query("SELECT tc.id FROM TradeCategory tc WHERE tc.parent.id = :parentId")
    List<Integer> findChildIdsByParentId(@Param("parentId") Integer parentId);

}
