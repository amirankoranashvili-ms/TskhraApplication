package com.tskhra.modulith.trade_module.model.domain;

import com.tskhra.modulith.trade_module.model.enums.TradeStatus;
import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.annotations.UpdateTimestamp;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "trade_offers")
public class TradeOffer {

    @Id
    @GeneratedValue
    private UUID id;

    @OneToOne
    @JoinColumn(name = "parent_id")
    private TradeOffer parent;

    // todo think about relationship + should trade be reset and new one created?
    private TradeChain tradeChain;

    @Column(nullable = false)
    private Long offererId;

    @Column(nullable = false)
    private Long responderId;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "status", columnDefinition = "trade_status")
    private TradeStatus status;

    private BigDecimal fairnessRatio;

    private LocalDateTime offererConfirmedAt;

    private LocalDateTime responderConfirmedAt;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;

}
