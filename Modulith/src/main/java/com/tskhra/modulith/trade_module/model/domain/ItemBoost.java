package com.tskhra.modulith.trade_module.model.domain;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "item_boosts")
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
public class ItemBoost {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "item_id", nullable = false)
    private Item item;

    @CreationTimestamp
    private LocalDateTime boostedAt;

    @Column(nullable = false)
    private Integer durationDays;

}
