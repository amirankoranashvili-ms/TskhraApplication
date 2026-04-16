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

    Page<TradeOffer> findAllByOffererId(Long offererId, Pageable pageable);

    Page<TradeOffer> findAllByResponderId(Long responderId, Pageable pageable);

    @Query("SELECT t FROM TradeOffer t WHERE t.offererId = :userId OR t.responderId = :userId")
    Page<TradeOffer> findAllByUserId(@Param("userId") Long userId, Pageable pageable);

    Page<TradeOffer> findAllByOffererIdAndStatus(Long offererId, TradeStatus status, Pageable pageable);

    Page<TradeOffer> findAllByResponderIdAndStatus(Long responderId, TradeStatus status, Pageable pageable);

    @Query("SELECT t FROM TradeOffer t WHERE (t.offererId = :userId OR t.responderId = :userId) AND t.status = :status")
    Page<TradeOffer> findAllByUserIdAndStatus(@Param("userId") Long userId, @Param("status") TradeStatus status, Pageable pageable);

    @Query("SELECT t FROM TradeOffer t WHERE t.status IN :statuses AND t.expiresAt < :now")
    List<TradeOffer> findExpiredOffers(@Param("statuses") List<TradeStatus> statuses, @Param("now") Instant now);
}