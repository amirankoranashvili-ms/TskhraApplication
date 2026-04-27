package com.tskhra.modulith.trade_module.repositories;

import com.tskhra.modulith.trade_module.model.domain.TradeChain;
import com.tskhra.modulith.trade_module.model.enums.ChainStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Repository
public interface TradeChainRepository extends JpaRepository<TradeChain, UUID> {

    @Query("SELECT DISTINCT c FROM TradeChain c JOIN c.links l " +
            "WHERE l.giverId = :userId OR l.receiverId = :userId")
    Page<TradeChain> findAllByParticipant(@Param("userId") Long userId, Pageable pageable);

    @Query("SELECT DISTINCT c FROM TradeChain c JOIN c.links l " +
            "WHERE (l.giverId = :userId OR l.receiverId = :userId) AND c.status = :status")
    Page<TradeChain> findAllByParticipantAndStatus(
            @Param("userId") Long userId, @Param("status") ChainStatus status, Pageable pageable);

    List<TradeChain> findAllByStatusAndExpiresAtBefore(ChainStatus status, Instant now);

}
