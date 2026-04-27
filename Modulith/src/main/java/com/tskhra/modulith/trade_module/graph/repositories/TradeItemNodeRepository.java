package com.tskhra.modulith.trade_module.graph.repositories;

import com.tskhra.modulith.trade_module.graph.nodes.TradeItemNode;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.data.neo4j.repository.query.Query;

import java.util.List;
import java.util.Map;
import java.util.Optional;

public interface TradeItemNodeRepository extends Neo4jRepository<TradeItemNode, String> {

    Optional<TradeItemNode> findByItemId(String itemId);

    @Query("MATCH (n:TradeItem {itemId: $itemId}) DETACH DELETE n")
    void deleteByItemId(String itemId);

    @Query("MATCH (n:TradeItem {status: 'AVAILABLE', categoryId: $categoryId}) " +
            "WHERE n.ownerId <> $excludeOwnerId RETURN n")
    List<TradeItemNode> findAvailableByCategoryIdExcludingOwner(Long categoryId, Long excludeOwnerId);

    @Query("MATCH (n:TradeItem {status: 'AVAILABLE', itemTypeId: $itemTypeId}) " +
            "WHERE n.ownerId <> $excludeOwnerId RETURN n")
    List<TradeItemNode> findAvailableByItemTypeIdExcludingOwner(Integer itemTypeId, Long excludeOwnerId);

    @Query("MATCH (n:TradeItem {status: 'AVAILABLE'}) " +
            "WHERE n.ownerId <> $excludeOwnerId " +
            "AND ANY(dc IN $desiredCategoryIds WHERE dc = n.categoryId) " +
            "RETURN n")
    List<TradeItemNode> findItemsWhoseDesiredCategoriesInclude(List<Long> desiredCategoryIds, Long excludeOwnerId);

    @Query("MATCH (n:TradeItem {itemId: $itemId})-[r:WANTS]->() DELETE r")
    void deleteOutgoingWants(String itemId);

    @Query("MATCH ()-[r:WANTS]->(n:TradeItem {itemId: $itemId}) DELETE r")
    void deleteIncomingWants(String itemId);

    @Query("MATCH (n:TradeItem {itemId: $itemId}) SET n.status = $status")
    void updateStatus(String itemId, String status);

    @Query("MATCH (n:TradeItem) RETURN count(n) AS nodeCount")
    long countNodes();

    @Query("MATCH ()-[r:WANTS]->() RETURN count(r) AS edgeCount")
    long countEdges();

}
