package com.tskhra.modulith.trade_module.model.domain;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "item_types")
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Getter
@Setter
public class ItemType {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private TradeCategory category;

    @Column(nullable = false)
    private String name;

    @Column(unique = true, nullable = false)
    private String slug;

}
