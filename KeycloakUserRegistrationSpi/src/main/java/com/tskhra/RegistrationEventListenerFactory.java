package com.tskhra;

import org.keycloak.Config;
import org.keycloak.events.EventListenerProvider;
import org.keycloak.events.EventListenerProviderFactory;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.KeycloakSessionFactory;

public class RegistrationEventListenerFactory implements EventListenerProviderFactory {
    @Override
    public EventListenerProvider create(KeycloakSession keycloakSession) {
        return new RegistrationEventListener(keycloakSession);
    }

    @Override
    public void init(Config.Scope scope) {
        // no need to implement
    }

    @Override
    public void postInit(KeycloakSessionFactory keycloakSessionFactory) {
        // no need to implement
    }

    @Override
    public void close() {
        // no need to implement
    }

    @Override
    public String getId() {
        return "my-registration-listener";
    }
}
