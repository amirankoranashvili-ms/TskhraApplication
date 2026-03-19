package com.tskhra.modulith.common.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.modulith.NamedInterface;

@NamedInterface
@ConfigurationProperties(prefix = "sumsub")
public record SumsubProperties(
        String baseUrl,
        String secretKey,
        String token,
        String levelName
) {
}
