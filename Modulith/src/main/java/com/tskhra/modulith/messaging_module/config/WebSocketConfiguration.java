package com.tskhra.modulith.messaging_module.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfiguration implements WebSocketMessageBrokerConfigurer {

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        // /ws is the HTTP URL for the endpoint to which a WebSocket (or SockJS)
        // client needs to connect for the WebSocket handshake.
        registry.addEndpoint("/ws")
                // Permits cross-origin requests
                .setAllowedOrigins("*")
                // Adds fallback support for browsers that don’t support native WebSockets
                // by emulating the behavior over HTTP.
//                .withSockJS()
        ;
    }

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        // STOMP messages whose destination header begins with /app are routed to
        // @MessageMapping methods in @Controller classes. It defines a namespace
        // for messages sent by clients, keeping them separate from broker destinations.
        registry.setApplicationDestinationPrefixes("/app");

        // Use the built-in message broker for subscriptions and broadcasting and
        // route messages whose destination header begins with /topic or /queue to the broker
        registry.enableSimpleBroker("/topic", "/queue")
                // This sends a heartbeat from the server every 10 seconds and expects
                // a response from the client every 20 seconds. If a client fails to
                // respond within the expected time frame, Spring Boot closes the
                // connection to free up resources.
//                .setHeartbeatValue(new long[] { 10000, 20000 })
        // Caused by: java.lang.IllegalArgumentException: Heartbeat values configured but no TaskScheduler provided
        ;
    }

}
