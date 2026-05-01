package com.tskhra.modulith.common.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.modulith.NamedInterface;

@NamedInterface
@ConfigurationProperties(prefix = "ai-service")
public record AiServiceProperties(
        String baseUrl,
        String apiKey
) {
}
