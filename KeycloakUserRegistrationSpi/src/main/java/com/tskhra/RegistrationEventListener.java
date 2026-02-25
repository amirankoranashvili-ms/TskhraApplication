package com.tskhra;

import org.keycloak.events.Event;
import org.keycloak.events.EventListenerProvider;
import org.keycloak.events.EventType;
import org.keycloak.events.admin.AdminEvent;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.RealmModel;
import org.keycloak.models.UserModel;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class RegistrationEventListener implements EventListenerProvider {

    private final KeycloakSession session;
    private final HttpClient httpClient;

    public RegistrationEventListener(KeycloakSession session) {
        this.session = session;
        this.httpClient = HttpClient.newHttpClient();
    }

    @Override
    public void onEvent(Event event) {
        if (EventType.REGISTER.equals(event.getType())) {
            System.out.println("EvenListener: REGISTER even caught");
            RealmModel realm = session.getContext().getRealm();
            UserModel user = session.users().getUserById(realm, event.getUserId());

            // todo send to api
            System.out.println("EvenListener: onEvent before sendUser");

            sendUser(user);
        }
    }

    private void sendUser(UserModel user) {
        System.out.println("EvenListener: sendUser start");

        String json = String.format(
                "{\"username\":\"%s\", \"email\":\"%s\", \"keycloakId\":\"%s\"}",
                user.getUsername(), user.getEmail(), user.getId()
        );

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://10.3.12.234:8081/users/kc-register"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

        System.out.println("EvenListener: sendUser beforeSend");

        httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenAccept(res -> System.out.println("External sync status: " + res.statusCode()));
    }

    @Override
    public void onEvent(AdminEvent adminEvent, boolean b) {

    }

    @Override
    public void close() {

    }
}
