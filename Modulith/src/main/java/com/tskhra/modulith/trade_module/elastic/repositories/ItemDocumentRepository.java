package com.tskhra.modulith.trade_module.elastic.repositories;

import com.tskhra.modulith.trade_module.elastic.documents.ItemDocument;
import org.springframework.data.elasticsearch.repository.ElasticsearchRepository;

import java.util.UUID;

public interface ItemDocumentRepository extends ElasticsearchRepository<ItemDocument, UUID> {
}