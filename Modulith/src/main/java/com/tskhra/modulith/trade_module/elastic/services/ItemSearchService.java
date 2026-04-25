package com.tskhra.modulith.trade_module.elastic.services;

import co.elastic.clients.elasticsearch._types.FieldValue;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.BoolQuery;
import co.elastic.clients.elasticsearch._types.query_dsl.Query;
import co.elastic.clients.elasticsearch._types.query_dsl.TextQueryType;
import com.tskhra.modulith.trade_module.model.enums.SortByDate;
import com.tskhra.modulith.common.services.ImageService;
import com.tskhra.modulith.trade_module.elastic.documents.ItemDocument;
import com.tskhra.modulith.trade_module.elastic.repositories.ItemDocumentRepository;
import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.requests.ItemSearchRequest;
import com.tskhra.modulith.trade_module.model.responses.ItemSummaryDto;
import com.tskhra.modulith.trade_module.repositories.CategorySwapRepository;
import com.tskhra.modulith.trade_module.repositories.ItemRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.elasticsearch.client.elc.NativeQuery;
import org.springframework.data.elasticsearch.client.elc.NativeQueryBuilder;
import org.springframework.data.elasticsearch.core.ElasticsearchOperations;
import org.springframework.data.elasticsearch.core.SearchHits;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class ItemSearchService {

    private final ElasticsearchOperations elasticsearchOperations;
    private final ItemDocumentRepository itemDocumentRepository;
    private final CategorySwapRepository categorySwapRepository;
    private final ItemRepository itemRepository;
    private final ImageService imageService;

    public Page<ItemSummaryDto> search(ItemSearchRequest request) {
        PageRequest pageRequest = PageRequest.of(request.page(), request.size());

        BoolQuery.Builder boolBuilder = new BoolQuery.Builder();

        // Always filter to AVAILABLE items only
        boolBuilder.filter(Query.of(q -> q.term(t -> t
                .field("status")
                .value(ItemStatus.AVAILABLE.name())
        )));

        // Full-text search on name and description
        if (request.query() != null && !request.query().isBlank()) {
            boolBuilder.must(Query.of(q -> q.multiMatch(m -> m
                    .query(request.query())
                    .fields("name^3", "description")
                    .type(TextQueryType.BestFields)
                    .fuzziness("AUTO")
                    .prefixLength(2)
                    .minimumShouldMatch("75%")
            )));
        }

        // Filter by category
        if (request.categoryId() != null) {
            boolean isParentCategory = categorySwapRepository.isParentCategoryById(request.categoryId());
            if (isParentCategory) {
                List<Long> childIds = categorySwapRepository.findChildIdsByParentId(request.categoryId());
                List<FieldValue> fieldValues = childIds.stream()
                        .map(FieldValue::of)
                        .toList();
                boolBuilder.filter(Query.of(q -> q.terms(t -> t
                        .field("categoryId")
                        .terms(tv -> tv.value(fieldValues))
                )));
            } else {
                boolBuilder.filter(Query.of(q -> q.term(t -> t
                        .field("categoryId")
                        .value(request.categoryId())
                )));
            }
        }

        // Filter by item type
        if (request.itemTypeId() != null) {
            boolBuilder.filter(Query.of(q -> q.term(t -> t
                    .field("itemTypeId")
                    .value(request.itemTypeId())
            )));
        }

        // Filter by city
        if (request.cityId() != null) {
            boolBuilder.filter(Query.of(q -> q.term(t -> t
                    .field("cityId")
                    .value(request.cityId())
            )));
        }

        // Filter by condition
        if (request.condition() != null) {
            boolBuilder.filter(Query.of(q -> q.term(t -> t
                    .field("condition")
                    .value(request.condition().name())
            )));
        }

        // Filter by trade range
        if (request.tradeRange() != null) {
            boolBuilder.filter(Query.of(q -> q.term(t -> t
                    .field("tradeRange")
                    .value(request.tradeRange().name())
            )));
        }

        // TODO: implement vipOnly filter once VIP status is available
        // if (request.vipOnly()) {
        //     boolBuilder.filter(Query.of(q -> q.term(t -> t
        //             .field("vipStatus")
        //             .value(true)
        //     )));
        // }

        SortOrder dateSortOrder = request.sortByDate() == SortByDate.OLDEST
                ? SortOrder.Asc : SortOrder.Desc;

        boolean hasTextQuery = request.query() != null && !request.query().isBlank();

        NativeQueryBuilder queryBuilder = NativeQuery.builder()
                .withQuery(Query.of(q -> q.bool(boolBuilder.build())))
                .withPageable(pageRequest);

        if (hasTextQuery) {
            queryBuilder.withSort(s -> s.score(sc -> sc.order(SortOrder.Desc)));
        }
        queryBuilder.withSort(s -> s.field(f -> f.field("updatedAt").order(dateSortOrder).missing("_last")));

        SearchHits<ItemDocument> searchHits = elasticsearchOperations.search(
                queryBuilder.build(), ItemDocument.class);

        List<ItemSummaryDto> results = searchHits.getSearchHits().stream()
                .map(hit -> toSummaryDto(hit.getContent()))
                .toList();

        return new PageImpl<>(results, pageRequest, searchHits.getTotalHits());
    }

    public List<String> suggest(String query, int limit) {
        BoolQuery.Builder boolBuilder = new BoolQuery.Builder();

        boolBuilder.filter(Query.of(q -> q.term(t -> t
                .field("status")
                .value(ItemStatus.AVAILABLE.name())
        )));

        boolBuilder.must(Query.of(q -> q.matchPhrasePrefix(m -> m
                .field("name")
                .query(query)
        )));

        NativeQuery nativeQuery = NativeQuery.builder()
                .withQuery(Query.of(q -> q.bool(boolBuilder.build())))
                .withPageable(PageRequest.of(0, limit))
                .build();

        SearchHits<ItemDocument> hits = elasticsearchOperations.search(nativeQuery, ItemDocument.class);

        return hits.getSearchHits().stream()
                .map(hit -> hit.getContent().getName())
                .distinct()
                .toList();
    }

    public void indexItem(Item item) {
        itemDocumentRepository.save(ItemDocument.fromEntity(item));
    }

    public void reindexItem(Item item) {
        itemDocumentRepository.save(ItemDocument.fromEntity(item));
    }

    public void updateItemStatus(UUID itemId, ItemStatus status) {
        itemDocumentRepository.findById(itemId).ifPresent(doc -> {
            doc.setStatus(status);
            itemDocumentRepository.save(doc);
        });
    }

    public void deleteFromIndex(UUID itemId) {
        itemDocumentRepository.deleteById(itemId);
    }

    public long bulkReindex() {
        List<Item> allItems = itemRepository.findAll();
        List<ItemDocument> documents = allItems.stream()
                .map(ItemDocument::fromEntity)
                .toList();
        itemDocumentRepository.saveAll(documents);
        log.info("Bulk re-indexed {} items into Elasticsearch", documents.size());
        return documents.size();
    }


    private ItemSummaryDto toSummaryDto(ItemDocument doc) {
        return new ItemSummaryDto(
                doc.getId(),
                doc.getOwnerId(),
                doc.getName(),
                doc.getDescription(),
                doc.getCategoryName(),
                doc.getCityName(),
                doc.getCondition(),
                doc.getTradeRange(),
                doc.getEstimatedValue(),
                doc.getCreatedAt(),
                doc.getImageUris() != null
                        ? doc.getImageUris().stream().map(imageService::getItemImageUrl).toList()
                        : List.of(),
                doc.getStatus(),
                false,
                doc.getItemTypeId(),
                doc.getItemTypeName(),
                doc.getSpecifications(),
                null
        );
    }
}
