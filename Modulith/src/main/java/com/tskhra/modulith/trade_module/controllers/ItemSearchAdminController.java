package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.elastic.services.ItemSearchService;
import io.swagger.v3.oas.annotations.Hidden;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@Tag(name = "Item Search Admin", description = "Administrative operations for item search index")
@RestController
@RequestMapping("/admin/search")
@RequiredArgsConstructor
public class ItemSearchAdminController {

    private final ItemSearchService itemSearchService;

    @Operation(summary = "Re-index all items from database into Elasticsearch")
    @Hidden
    @PostMapping("/bulk-reindex")
    public ResponseEntity<Map<String, Object>> bulkReindex() {
        long count = itemSearchService.bulkReindex();
        return ResponseEntity.ok(Map.of("reindexed", count));
    }
}
