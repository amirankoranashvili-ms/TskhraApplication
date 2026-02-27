package com.tskhra.modulith.user_module.services;

import com.tskhra.modulith.common.properties.KeycloakProperties;
import com.tskhra.modulith.user_module.exception.HttpBadRequestException;
import com.tskhra.modulith.user_module.exception.HttpUnauthorizedException;
import com.tskhra.modulith.user_module.model.requests.LoginRequestDto;
import com.tskhra.modulith.user_module.model.requests.RefreshTokenRequest;
import com.tskhra.modulith.user_module.model.responses.TokensResponse;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpRequest;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.http.client.ClientHttpResponse;
import org.springframework.stereotype.Service;
import org.springframework.util.ErrorHandler;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.ResponseErrorHandler;
import org.springframework.web.client.RestClient;

import java.io.IOException;
import java.util.function.BiConsumer;
import java.util.function.Predicate;
import java.util.function.Supplier;

@Service
public class AuthService {

    private final KeycloakProperties keycloakProperties;
    private final RestClient restClient;

    public AuthService(KeycloakProperties keycloakProperties, RestClient.Builder restClientBuilder) {
        this.keycloakProperties = keycloakProperties;

        String tokenUrl = String.format("%s/realms/%s/protocol/openid-connect/token",
                keycloakProperties.serverUrl(), keycloakProperties.realm());

        this.restClient = restClientBuilder
                .baseUrl(tokenUrl)
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_FORM_URLENCODED_VALUE)
                .build();
    }

    public TokensResponse login(LoginRequestDto dto) {
        MultiValueMap<String, String> formData = new LinkedMultiValueMap<>();
        formData.add("client_id", keycloakProperties.clientId());
        formData.add("client_secret", keycloakProperties.clientSecret());
        formData.add("grant_type", "password");
        formData.add("username", dto.username());
        formData.add("password", dto.password());

        return restClient.post()
                .body(formData)
                .retrieve()
                .onStatus(_401, throw401)
                .body(TokensResponse.class);
    }

    public TokensResponse refreshToken(RefreshTokenRequest dto) {
        MultiValueMap<String, String> formData = new LinkedMultiValueMap<>();
        formData.add("grant_type", "refresh_token");
        formData.add("client_id", keycloakProperties.clientId());
        formData.add("client_secret", keycloakProperties.clientSecret());
        formData.add("refresh_token", dto.refreshToken());

        return restClient.post()
                .body(formData)
                .retrieve()
                .onStatus(_400, throw400)
                .body(TokensResponse.class);
    }

    private static final Predicate<HttpStatusCode> _400 = code -> code.value() == 400;
    private static final Predicate<HttpStatusCode> _401 = code -> code.value() == 401;

    private static final RestClient.ResponseSpec.ErrorHandler throw400 = (req, resp) -> {
        throw new HttpBadRequestException("Invalid refresh token.");
    };

    private static final RestClient.ResponseSpec.ErrorHandler throw401 = (req, resp) -> {
        throw new HttpUnauthorizedException("Invalid credentials.");
    };

}
