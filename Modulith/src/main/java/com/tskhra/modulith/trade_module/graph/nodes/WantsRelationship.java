package com.tskhra.modulith.trade_module.graph.nodes;

import lombok.*;
import org.springframework.data.neo4j.core.schema.RelationshipId;
import org.springframework.data.neo4j.core.schema.RelationshipProperties;
import org.springframework.data.neo4j.core.schema.TargetNode;

@RelationshipProperties
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Getter
@Setter
public class WantsRelationship {

    @RelationshipId
    private Long id;

    @TargetNode
    private TradeItemNode targetItem;

    private String matchLevel;
    private Double weight;

}
