package com.tskhra.modulith.booking_module.controllers;

import com.tskhra.modulith.booking_module.model.requests.ChatbotSubmitRequest;
import com.tskhra.modulith.booking_module.model.responses.ChatbotConfigDto;
import com.tskhra.modulith.booking_module.services.ChatbotService;
import io.swagger.v3.oas.annotations.Operation;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/chatbot")
@RequiredArgsConstructor
public class ChatbotController {

    private final ChatbotService chatbotService;

    @Operation(summary = "Get chatbot onboarding questions by category")
    @GetMapping("/questions")
    public ResponseEntity<List<String>> getQuestions(@AuthenticationPrincipal Jwt jwt,
                                                     @RequestParam String category) {
        List<String> questions = chatbotService.getQuestions(category);
        return ResponseEntity.ok(questions);
    }

    @Operation(summary = "Submit chatbot answers for a business")
    @PostMapping("/answers")
    public ResponseEntity<ChatbotConfigDto> submitAnswers(@AuthenticationPrincipal Jwt jwt,
                                                          @Valid @RequestBody ChatbotSubmitRequest request) {
        ChatbotConfigDto config = chatbotService.submitAnswers(request, jwt);
        return ResponseEntity.status(HttpStatus.CREATED).body(config);
    }

    @Operation(summary = "Get chatbot configuration for a business")
    @GetMapping("/{businessId}")
    public ResponseEntity<ChatbotConfigDto> getChatbotConfig(@AuthenticationPrincipal Jwt jwt,
                                                              @PathVariable Long businessId) {
        ChatbotConfigDto config = chatbotService.getChatbotConfig(businessId, jwt);
        return ResponseEntity.ok(config);
    }
}
