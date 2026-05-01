package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.requests.OnboardingGenerateRequest;
import com.tskhra.modulith.booking_module.model.responses.OnboardingGenerateResponse;
import com.tskhra.modulith.booking_module.model.responses.QuestionsResponse;
import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.properties.AiServiceProperties;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
@Slf4j
public class AiServiceClient {

    private final RestClient restClient;

    public AiServiceClient(AiServiceProperties aiServiceProperties, RestClient.Builder restClientBuilder) {
        this.restClient = restClientBuilder.baseUrl(aiServiceProperties.baseUrl()).build();
    }

    public QuestionsResponse getQuestions(String category) {
        try {
            QuestionsResponse response = restClient.get()
                    .uri("/api/onboarding/questions/{category}", category)
                    .retrieve()
                    .body(QuestionsResponse.class);

            if (response == null) {
                throw new HttpBadRequestException("AI service returned empty response");
            }

            return response;
        } catch (HttpBadRequestException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to fetch questions for category: {}", category, e);
            throw new HttpBadRequestException("AI service is currently unavailable. Please try again later.");
        }
    }

    public OnboardingGenerateResponse generateOnboarding(OnboardingGenerateRequest request) {
        try {
            OnboardingGenerateResponse response = restClient.post()
                    .uri("/api/onboarding/generate")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .body(OnboardingGenerateResponse.class);

            if (response == null) {
                throw new HttpBadRequestException("AI service returned empty response");
            }

            return response;
        } catch (HttpBadRequestException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to generate onboarding for businessId: {}", request.businessId(), e);
            throw new HttpBadRequestException("AI service is currently unavailable. Please try again later.");
        }
    }
}
