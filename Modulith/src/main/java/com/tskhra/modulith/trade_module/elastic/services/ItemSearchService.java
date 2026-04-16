package com.tskhra.modulith.trade_module.elastic.services;

import co.elastic.clients.elasticsearch._types.query_dsl.BoolQuery;
import co.elastic.clients.elasticsearch._types.query_dsl.Query;
import com.tskhra.modulith.common.services.ImageService;
import com.tskhra.modulith.trade_module.elastic.documents.ItemDocument;
import com.tskhra.modulith.trade_module.elastic.repositories.ItemDocumentRepository;
import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.requests.ItemSearchRequest;
import com.tskhra.modulith.trade_module.model.responses.ItemSummaryDto;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.elasticsearch.client.elc.NativeQuery;
import org.springframework.data.elasticsearch.core.ElasticsearchOperations;
import org.springframework.data.elasticsearch.core.SearchHits;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ItemSearchService {

    private final ElasticsearchOperations elasticsearchOperations;
    private final ItemDocumentRepository itemDocumentRepository;
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
                    .fields("name", "description")
            )));
        }

        // Filter by category
        if (request.categoryId() != null) {
            boolBuilder.filter(Query.of(q -> q.term(t -> t
                    .field("categoryId")
                    .value(request.categoryId())
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

        // Filter by price range
        if (request.minPrice() != null || request.maxPrice() != null) {
            boolBuilder.filter(Query.of(q -> q.range(r -> {
                var rangeQuery = r.number(n -> {
                    n.field("estimatedValue");
                    if (request.minPrice() != null) {
                        n.gte(request.minPrice().doubleValue());
                    }
                    if (request.maxPrice() != null) {
                        n.lte(request.maxPrice().doubleValue());
                    }
                    return n;
                });
                return r;
            })));
        }

        NativeQuery query = NativeQuery.builder()
                .withQuery(Query.of(q -> q.bool(boolBuilder.build())))
                .withPageable(pageRequest)
                .build();

        SearchHits<ItemDocument> searchHits = elasticsearchOperations.search(query, ItemDocument.class);

        List<ItemSummaryDto> results = searchHits.getSearchHits().stream()
                .map(hit -> toSummaryDto(hit.getContent()))
                .toList();

        return new PageImpl<>(results, pageRequest, searchHits.getTotalHits());
    }

    public void indexItem(Item item) {
        itemDocumentRepository.save(ItemDocument.fromEntity(item));
    }

    public void updateItemStatus(UUID itemId, ItemStatus status) {
        itemDocumentRepository.findById(itemId).ifPresent(doc -> {
            doc.setStatus(status);
            itemDocumentRepository.save(doc);
        });
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
                doc.getStatus()
        );
    }
}
