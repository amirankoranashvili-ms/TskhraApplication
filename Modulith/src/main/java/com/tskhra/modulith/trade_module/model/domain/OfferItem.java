package com.tskhra.modulith.trade_module.model.domain;

import com.tskhra.modulith.trade_module.model.enums.OwningSide;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "offer_items")
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
public class OfferItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "item_id")
    private Item item;

    @ManyToOne
    @JoinColumn(name = "offer_id")
    private TradeOffer tradeOffer;

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "owning_side", columnDefinition = "owning_side")
    private OwningSide owningSide;

    public OfferItem(Item i, TradeOffer tradeOffer, OwningSide owningSide) {
        this.item = i;
        this.tradeOffer = tradeOffer;
        this.owningSide = owningSide;
    }
}
