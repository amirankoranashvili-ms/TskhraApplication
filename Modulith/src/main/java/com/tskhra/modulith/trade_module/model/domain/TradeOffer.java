package com.tskhra.modulith.trade_module.model.domain;

import com.tskhra.modulith.trade_module.model.enums.TradeStatus;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.annotations.UpdateTimestamp;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "trade_offers")
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
public class TradeOffer {

    @Id
    @GeneratedValue
    private UUID id;

    @OneToOne
    @JoinColumn(name = "parent_id")
    private TradeOffer parent;

   @ManyToOne(fetch = FetchType.LAZY)
   @JoinColumn(name = "trade_chain_id")
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
