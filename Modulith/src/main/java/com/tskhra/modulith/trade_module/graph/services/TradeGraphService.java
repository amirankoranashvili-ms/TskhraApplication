package com.tskhra.modulith.trade_module.graph.services;

import com.tskhra.modulith.trade_module.graph.nodes.TradeItemNode;
import com.tskhra.modulith.trade_module.graph.repositories.TradeItemNodeRepository;
import com.tskhra.modulith.trade_module.model.domain.TradeCategory;
import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.domain.ItemDesiredType;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.repositories.ItemDesiredTypeRepository;
import com.tskhra.modulith.trade_module.repositories.ItemRepository;
import com.tskhra.modulith.trade_module.repositories.TradeCategoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Lazy;
import org.springframework.data.neo4j.core.Neo4jClient;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@Service
@RequiredArgsConstructor
@Slf4j
public class TradeGraphService {

    private final TradeItemNodeRepository nodeRepository;
    private final Neo4jClient neo4jClient;
    private final ItemRepository itemRepository;
    private final ItemDesiredTypeRepository desiredTypeRepository;
    private final TradeCategoryRepository tradeCategoryRepository;

    private TradeGraphService self;

    @Lazy
    @org.springframework.beans.factory.annotation.Autowired
    public void setSelf(TradeGraphService self) {
        this.self = self;
    }

    @Transactional("neo4jTransactionManager")
    public void syncItem(Item item) {
        List<Integer> desiredCategoryIds = item.getDesiredCategories() != null
                ? expandCategoryIds(item.getDesiredCategories().stream().map(TradeCategory::getId).toList())
                : Collections.emptyList();

        List<ItemDesiredType> desiredTypes = desiredTypeRepository.findAllByItemId(item.getId());
        List<Integer> desiredItemTypeIds = desiredTypes.stream()
                .map(dt -> dt.getItemType().getId())
                .toList();

        TradeItemNode node = nodeRepository.findByItemId(item.getId().toString()).orElse(null);
        if (node == null) {
            node = new TradeItemNode();
            node.setItemId(item.getId().toString());
        }

        node.setOwnerId(item.getOwnerId());
        node.setName(item.getName());
        node.setCategoryId(item.getCategory() != null ? item.getCategory().getId() : null);
        node.setCategoryName(item.getCategory() != null ? item.getCategory().getName() : null);
        node.setItemTypeId(item.getItemType() != null ? item.getItemType().getId() : null);
        node.setStatus(item.getStatus().name());
        node.setEstimatedValue(item.getEstimatedValue());
        node.setCityName(item.getCity() != null ? item.getCity().getName() : null);
        node.setTradeRange(item.getTradeRange() != null ? item.getTradeRange().name() : null);
        node.setDesiredCategoryIds(desiredCategoryIds);
        node.setDesiredItemTypeIds(desiredItemTypeIds);

        nodeRepository.save(node);
    }

    @Transactional("neo4jTransactionManager")
    public void computeEdges(Item item) {
        String itemId = item.getId().toString();

        nodeRepository.deleteOutgoingWants(itemId);

        List<Integer> desiredCategoryIds = item.getDesiredCategories() != null
                ? expandCategoryIds(item.getDesiredCategories().stream().map(TradeCategory::getId).toList())
                : Collections.emptyList();

        List<ItemDesiredType> desiredTypes = desiredTypeRepository.findAllByItemId(item.getId());
        List<Integer> desiredItemTypeIds = desiredTypes.stream()
                .map(dt -> dt.getItemType().getId())
                .toList();

        Long ownerId = item.getOwnerId();
        Integer categoryId = item.getCategory() != null ? item.getCategory().getId() : null;
        Integer parentCategoryId = item.getCategory() != null && item.getCategory().getParent() != null
                ? item.getCategory().getParent().getId() : null;

        if (!desiredCategoryIds.isEmpty()) {
            neo4jClient.query("""
                    MATCH (source:TradeItem {itemId: $sourceId}), (target:TradeItem {status: 'AVAILABLE'})
                    WHERE target.categoryId IN $desiredCategoryIds
                      AND target.ownerId <> $ownerId
                      AND target.itemId <> $sourceId
                    CREATE (source)-[:WANTS {matchLevel: 'CATEGORY', weight: 0.5}]->(target)
                    """)
                    .bind(itemId).to("sourceId")
                    .bind(desiredCategoryIds).to("desiredCategoryIds")
                    .bind(ownerId).to("ownerId")
                    .run();
        }

        if (!desiredItemTypeIds.isEmpty()) {
            neo4jClient.query("""
                    MATCH (source:TradeItem {itemId: $sourceId}), (target:TradeItem {status: 'AVAILABLE'})
                    WHERE target.itemTypeId IN $desiredItemTypeIds
                      AND target.ownerId <> $ownerId
                      AND target.itemId <> $sourceId
                      AND NOT EXISTS { (source)-[:WANTS]->(target) }
                    CREATE (source)-[:WANTS {matchLevel: 'ITEM_TYPE', weight: 0.8}]->(target)
                    """)
                    .bind(itemId).to("sourceId")
                    .bind(desiredItemTypeIds).to("desiredItemTypeIds")
                    .bind(ownerId).to("ownerId")
                    .run();
        }

        if (categoryId != null) {
            neo4jClient.query("""
                    MATCH (source:TradeItem {status: 'AVAILABLE'}), (target:TradeItem {itemId: $targetId})
                    WHERE $categoryId IN source.desiredCategoryIds
                      AND source.ownerId <> $ownerId
                      AND source.itemId <> $targetId
                      AND NOT EXISTS { (source)-[:WANTS]->(target) }
                    CREATE (source)-[:WANTS {matchLevel: 'CATEGORY', weight: 0.5}]->(target)
                    """)
                    .bind(itemId).to("targetId")
                    .bind(categoryId).to("categoryId")
                    .bind(ownerId).to("ownerId")
                    .run();
        }

        Integer itemTypeId = item.getItemType() != null ? item.getItemType().getId() : null;
        if (itemTypeId != null) {
            neo4jClient.query("""
                    MATCH (source:TradeItem {status: 'AVAILABLE'}), (target:TradeItem {itemId: $targetId})
                    WHERE $itemTypeId IN source.desiredItemTypeIds
                      AND source.ownerId <> $ownerId
                      AND source.itemId <> $targetId
                      AND NOT EXISTS { (source)-[:WANTS]->(target) }
                    CREATE (source)-[:WANTS {matchLevel: 'ITEM_TYPE', weight: 0.8}]->(target)
                    """)
                    .bind(itemId).to("targetId")
                    .bind(itemTypeId).to("itemTypeId")
                    .bind(ownerId).to("ownerId")
                    .run();
        }

        log.info("Computed edges for item {}", itemId);
    }

    @Transactional("neo4jTransactionManager")
    public void removeEdgesForItem(UUID itemId) {
        String id = itemId.toString();
        nodeRepository.deleteOutgoingWants(id);
        nodeRepository.deleteIncomingWants(id);
    }

    @Transactional("neo4jTransactionManager")
    public void updateNodeStatus(UUID itemId, ItemStatus status) {
        nodeRepository.updateStatus(itemId.toString(), status.name());
    }

    @Transactional("neo4jTransactionManager")
    public void removeNode(UUID itemId) {
        nodeRepository.deleteByItemId(itemId.toString());
    }

    @Transactional(value = "neo4jTransactionManager", readOnly = true)
    public List<Map<String, Object>> findChains(UUID itemId, int maxResults) {
        return neo4jClient.query("""
                MATCH path = (start:TradeItem {itemId: $itemId})-[:WANTS*2..6]->(start)
                WITH path, nodes(path)[0..-1] AS ns
                WHERE ALL(n IN ns WHERE n.status = 'AVAILABLE')
                  AND ALL(i IN range(0, size(ns)-1) WHERE
                    NONE(j IN range(i+1, size(ns)-1) WHERE ns[i].ownerId = ns[j].ownerId))
                RETURN [n IN ns | {
                  itemId: n.itemId,
                  ownerId: n.ownerId,
                  name: n.name,
                  categoryName: n.categoryName,
                  estimatedValue: n.estimatedValue
                }] AS chain,
                size(ns) AS chainLength
                ORDER BY chainLength ASC
                LIMIT $maxResults
                """)
                .bind(itemId.toString()).to("itemId")
                .bind(maxResults).to("maxResults")
                .fetch().all().stream()
                .toList();
    }

    @Transactional("neo4jTransactionManager")
    public void rebuildGraph() {
        log.info("Rebuilding trade graph...");
        neo4jClient.query("MATCH (n:TradeItem) DETACH DELETE n").run();

        List<Item> availableItems = itemRepository.findAllByStatus(ItemStatus.AVAILABLE);
        log.info("Found {} available items to index", availableItems.size());

        for (Item item : availableItems) {
            self.syncItem(item);
        }

        for (Item item : availableItems) {
            self.computeEdges(item);
        }

        log.info("Graph rebuild complete: {} nodes, {} edges",
                nodeRepository.countNodes(), nodeRepository.countEdges());
    }

    private List<Integer> expandCategoryIds(List<Integer> categoryIds) {
        Set<Integer> expanded = new LinkedHashSet<>(categoryIds);
        for (Integer id : categoryIds) {
            if (tradeCategoryRepository.isParentCategoryById(id)) {
                expanded.addAll(tradeCategoryRepository.findChildIdsByParentId(id));
            }
        }
        return List.copyOf(expanded);
    }

    @Transactional(value = "neo4jTransactionManager", readOnly = true)
    public Map<String, Long> getStats() {
        return Map.of(
                "nodes", nodeRepository.countNodes(),
                "edges", nodeRepository.countEdges()
        );
    }

}
