package com.tskhra.modulith.trade_module.model.domain;

import com.tskhra.modulith.trade_module.model.enums.ChainStatus;
import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "trade_chains")
public class TradeChain {

    @Id
    @GeneratedValue
    private UUID id;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "status", columnDefinition = "chain_status")
    private ChainStatus status;

    @CreationTimestamp
    private LocalDateTime createdAt;

}
