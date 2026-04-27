package com.tskhra.modulith.common.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.neo4j.repository.config.EnableNeo4jRepositories;

@Configuration
@EnableNeo4jRepositories(
        basePackages = "com.tskhra.modulith.trade_module.graph.repositories",
        transactionManagerRef = "neo4jTransactionManager"
)
public class Neo4jConfig {
}
