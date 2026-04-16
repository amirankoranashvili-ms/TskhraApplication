package com.tskhra.modulith.common.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.modulith.NamedInterface;

@NamedInterface
@ConfigurationProperties(prefix = "elasticsearch")
public record ElasticsearchProperties(
        String itemIndexName,
        int maxResultWindow
) {
}
