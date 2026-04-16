package com.tskhra.modulith.trade_module.repositories;

import com.tskhra.modulith.trade_module.model.domain.TradeOffer;
import com.tskhra.modulith.trade_module.model.enums.TradeStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Repository
public interface TradeOfferRepository extends JpaRepository<TradeOffer, UUID> {

    @Query("SELECT DISTINCT t FROM TradeOffer t JOIN t.offerItems oi WHERE oi.item.id IN :itemIds AND t.status = :status")
    List<TradeOffer> findAllByItemIdsAndStatus(@Param("itemIds") List<UUID> itemIds, @Param("status") TradeStatus status);

    @Query("SELECT t FROM TradeOffer t WHERE (t.offererId = :userId OR t.responderId = :userId)")
    Page<TradeOffer> findAllByUserId(@Param("userId") Long userId, Pageable pageable);

    @Query("""
            SELECT t FROM TradeOffer t
            WHERE (:direction = 'SENT' AND t.offererId = :userId
                OR :direction = 'RECEIVED' AND t.responderId = :userId
                OR :direction IS NULL AND (t.offererId = :userId OR t.responderId = :userId))
            AND (:status IS NULL OR t.status = :status)
            """)
    Page<TradeOffer> findByUserFiltered(
            @Param("userId") Long userId,
            @Param("direction") String direction,
            @Param("status") TradeStatus status,
            Pageable pageable);

    @Query("SELECT t FROM TradeOffer t WHERE t.status IN :statuses AND t.expiresAt < :now")
    List<TradeOffer> findExpiredOffers(@Param("statuses") List<TradeStatus> statuses, @Param("now") Instant now);
}