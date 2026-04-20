package com.tskhra.modulith.trade_module.repositories;

import com.tskhra.modulith.trade_module.model.domain.CategorySwap;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CategorySwapRepository extends JpaRepository<CategorySwap, Long> {

    @Query("SELECT COUNT(cs) > 0 FROM CategorySwap cs WHERE cs.parent.id = :categoryId")
    boolean isParentCategoryById(@Param("categoryId") Long categoryId);

    @Query("SELECT cs.id FROM CategorySwap cs WHERE cs.parent.id = :parentId")
    List<Long> findChildIdsByParentId(@Param("parentId") Long parentId);
}