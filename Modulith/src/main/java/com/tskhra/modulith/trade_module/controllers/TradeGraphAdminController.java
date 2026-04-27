package com.tskhra.modulith.trade_module.controllers;

import com.tskhra.modulith.trade_module.graph.services.TradeGraphService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@Tag(name = "Trade Graph Admin", description = "Manage trade graph in Neo4j")
@RestController
@RequestMapping("/admin/trade-graph")
@RequiredArgsConstructor
public class TradeGraphAdminController {

    private final TradeGraphService graphService;

    @Operation(summary = "Rebuild the entire trade graph from PostgreSQL")
    @PostMapping("/rebuild")
    public ResponseEntity<Map<String, Long>> rebuild() {
        graphService.rebuildGraph();
        return ResponseEntity.ok(graphService.getStats());
    }

    @Operation(summary = "Get trade graph statistics")
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Long>> stats() {
        return ResponseEntity.ok(graphService.getStats());
    }

}
