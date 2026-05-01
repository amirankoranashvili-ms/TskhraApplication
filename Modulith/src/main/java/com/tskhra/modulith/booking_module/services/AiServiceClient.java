package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.requests.OnboardingGenerateRequest;
import com.tskhra.modulith.booking_module.model.requests.ProviderCreateRequest;
import com.tskhra.modulith.booking_module.model.responses.ProviderCreateResponse;
import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.properties.AiServiceProperties;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.List;

@Service
@Slf4j
public class AiServiceClient {

    private final AiServiceProperties aiServiceProperties;
    private final RestClient restClient;

    public AiServiceClient(AiServiceProperties aiServiceProperties, RestClient.Builder restClientBuilder) {
        this.aiServiceProperties = aiServiceProperties;
        this.restClient = restClientBuilder.baseUrl(aiServiceProperties.baseUrl()).build();
    }

    @SuppressWarnings("unchecked")
    public List<String> getQuestions(String category) {
        try {
            return restClient.get()
                    .uri("/api/onboarding/questions/{category}", category)
                    .retrieve()
                    .body(List.class);
        } catch (Exception e) {
            log.error("Failed to fetch questions for category: {}", category, e);
            throw new HttpBadRequestException("AI service is currently unavailable. Please try again later.");
        }
    }

    public ProviderCreateResponse createProvider(ProviderCreateRequest request) {
        try {
            ProviderCreateResponse response = restClient.post()
                    .uri("/api/providers")
                    .contentType(MediaType.APPLICATION_JSON)
                    .header("X-API-Key", aiServiceProperties.apiKey())
                    .body(request)
                    .retrieve()
                    .body(ProviderCreateResponse.class);

            if (response == null) {
                throw new HttpBadRequestException("AI service returned empty response");
            }

            return response;
        } catch (HttpBadRequestException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to create AI provider for businessId: {}", request.businessId(), e);
            throw new HttpBadRequestException("AI service is currently unavailable. Please try again later.");
        }
    }

    public void generateOnboarding(OnboardingGenerateRequest request) {
        try {
            restClient.post()
                    .uri("/api/onboarding/generate")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .toBodilessEntity();
        } catch (Exception e) {
            log.error("Failed to generate onboarding for businessId: {}", request.businessId(), e);
            throw new HttpBadRequestException("AI service is currently unavailable. Please try again later.");
        }
    }
}
