package com.tskhra.modulith.common.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.modulith.NamedInterface;

@NamedInterface
@ConfigurationProperties(prefix = "rabbitmq.stomp")
public record RabbitStompProperties(
        String host,
        int port,
        String login,
        String passcode
) {
}
