package com.tskhra.modulith.trade_module.model.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "chain_links")
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Getter
@Setter
public class ChainLink {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "chain_id", nullable = false)
    private TradeChain chain;

    @Column(nullable = false)
    private Integer position;

    @Column(nullable = false)
    private Long giverId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "item_id", nullable = false)
    private Item item;

    @Column(nullable = false)
    private Long receiverId;

    private LocalDateTime acceptedAt;

    private LocalDateTime confirmedAt;

}
