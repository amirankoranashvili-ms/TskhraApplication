package com.tskhra.modulith.trade_module.graph.nodes;

import lombok.*;
import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.Node;
import org.springframework.data.neo4j.core.schema.Relationship;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

@Node("TradeItem")
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Getter
@Setter
public class TradeItemNode {

    @Id
    private String itemId;

    private Long ownerId;
    private String name;
    private Long categoryId;
    private String categoryName;
    private Integer itemTypeId;
    private String status;
    private BigDecimal estimatedValue;
    private String cityName;
    private String tradeRange;

    @Builder.Default
    private List<Long> desiredCategoryIds = Collections.emptyList();

    @Builder.Default
    private List<Integer> desiredItemTypeIds = Collections.emptyList();

    @Relationship(type = "WANTS", direction = Relationship.Direction.OUTGOING)
    @Builder.Default
    private List<WantsRelationship> wants = new ArrayList<>();

}
