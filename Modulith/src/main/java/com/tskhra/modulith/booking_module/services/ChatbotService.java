package com.tskhra.modulith.booking_module.services;

import com.tskhra.modulith.booking_module.model.domain.Business;
import com.tskhra.modulith.booking_module.model.domain.BusinessChatbot;
import com.tskhra.modulith.booking_module.model.requests.ChatbotSubmitRequest;
import com.tskhra.modulith.booking_module.model.requests.OnboardingGenerateRequest;
import com.tskhra.modulith.booking_module.model.responses.ChatbotConfigDto;
import com.tskhra.modulith.booking_module.model.responses.OnboardingGenerateResponse;
import com.tskhra.modulith.booking_module.model.responses.QuestionsResponse;
import com.tskhra.modulith.booking_module.repositories.BusinessChatbotRepository;
import com.tskhra.modulith.booking_module.repositories.BusinessRepository;
import com.tskhra.modulith.common.exception.http_exceptions.HttpBadRequestException;
import com.tskhra.modulith.common.exception.http_exceptions.HttpForbiddenError;
import com.tskhra.modulith.common.exception.http_exceptions.HttpNotFoundException;
import com.tskhra.modulith.user_module.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ChatbotService {

    private final BusinessChatbotRepository businessChatbotRepository;
    private final BusinessRepository businessRepository;
    private final UserService userService;
    private final AiServiceClient aiServiceClient;

    public QuestionsResponse getQuestions(String category) {
        return aiServiceClient.getQuestions(category);
    }

    @Transactional
    public ChatbotConfigDto submitAnswers(ChatbotSubmitRequest request, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();

        Business business = businessRepository.findById(request.businessId())
                .orElseThrow(() -> new HttpNotFoundException("Business not found with id: " + request.businessId()));

        if (!business.getUserId().equals(userId)) {
            throw new HttpForbiddenError("You are not authorized to manage this business's chatbot");
        }

        if (business.getCategory() == null) {
            throw new HttpBadRequestException("Business must have a category before configuring a chatbot");
        }

        String categoryName = business.getCategory().getName();

        OnboardingGenerateRequest generateRequest = new OnboardingGenerateRequest(
                business.getId(),
                categoryName,
                request.answers()
        );
        OnboardingGenerateResponse generateResponse = aiServiceClient.generateOnboarding(generateRequest);

        BusinessChatbot chatbot = businessChatbotRepository.findByBusinessId(request.businessId())
                .orElse(BusinessChatbot.builder().business(business).build());

        chatbot.setAiProviderId(generateResponse.providerId());
        chatbot.setChatApiKey(generateResponse.chatApiKey());
        businessChatbotRepository.save(chatbot);

        return new ChatbotConfigDto(generateResponse.providerId(), generateResponse.chatApiKey());
    }

    public ChatbotConfigDto getChatbotConfig(Long businessId, Jwt jwt) {
        Long userId = userService.getCurrentUser(jwt).getId();

        Business business = businessRepository.findById(businessId)
                .orElseThrow(() -> new HttpNotFoundException("Business not found with id: " + businessId));

        if (!business.getUserId().equals(userId)) {
            throw new HttpForbiddenError("You are not authorized to view this business's chatbot config");
        }

        BusinessChatbot chatbot = businessChatbotRepository.findByBusinessId(businessId)
                .orElseThrow(() -> new HttpNotFoundException("Chatbot not configured for business: " + businessId));

        return new ChatbotConfigDto(chatbot.getAiProviderId(), chatbot.getChatApiKey());
    }
}
