package com.tskhra.modulith.messaging_module.config;

import org.jspecify.annotations.Nullable;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.WebSocketHandler;
import org.springframework.web.socket.server.support.DefaultHandshakeHandler;

import java.security.Principal;
import java.util.Map;

@Component
public class UserHandshakeHandler extends DefaultHandshakeHandler {

    @Override
    protected @Nullable Principal determineUser(ServerHttpRequest request, WebSocketHandler wsHandler,
                                                Map<String, Object> attributes) {

        Object keycloakId = attributes.get("userId");
        return keycloakId == null ? null : new StompPrincipal(keycloakId.toString());
    }
}
