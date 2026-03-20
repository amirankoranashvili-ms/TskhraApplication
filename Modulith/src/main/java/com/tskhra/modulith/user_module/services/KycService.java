package com.tskhra.modulith.user_module.services;

import com.tskhra.modulith.common.properties.SumsubProperties;
import com.tskhra.modulith.user_module.model.requests.SumsubWebhookPayload;
import com.tskhra.modulith.user_module.model.responses.KycTokenResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Map;

@Service
@Slf4j
public class KycService {

    private final SumsubProperties sumsubProperties;
    private final RestClient restClient;
    private final UserService userService;

    private static final String TOKEN_PATH = "/resources/accessTokens/sdk";
    public static final String APPLICANT_INFO_PATH = "/resources/applicants/{applicantId}/one";


    public KycService(SumsubProperties sumsubProperties, RestClient.Builder restClientBuilder, UserService userService) {
        this.sumsubProperties = sumsubProperties;
        this.restClient = restClientBuilder.baseUrl(sumsubProperties.baseUrl())
                .build();
        this.userService = userService;
    }


    public KycTokenResponse getAccessToken(Jwt jwt) {
        String userId = jwt.getClaimAsString("sub");
        String timestamp = String.valueOf(Instant.now().getEpochSecond());
        String levelName = sumsubProperties.levelName();
        String appToken = sumsubProperties.token();

        log.info("Timestamp: {}", timestamp);
        log.info("User idd: {}", userId);

        String jsonBody = """
                {
                  "userId": "%s",
                  "levelName": "%s",
                  "ttlInSecs": 600
                }
                """.formatted(userId, levelName).trim();

        log.info("Json body: {}", jsonBody);

        String signature = createSignature(timestamp, "POST", TOKEN_PATH, jsonBody);
        log.info("Signature: {}", signature);

        Map response = restClient.post()
                .uri(TOKEN_PATH)
                .contentType(MediaType.APPLICATION_JSON)
                .header("X-App-Token", appToken)
                .header("X-App-Access-Ts", timestamp)
                .header("X-App-Access-Sig", signature)
                .body(jsonBody)
                .retrieve()
                .body(Map.class);

        if (response == null || !response.containsKey("token")) {
            throw new RuntimeException("Error getting access token from Sumsub.");
        }

        String token = (String) response.get("token");
        log.info("Token: {}", token);
        return new KycTokenResponse(token, userId);
    }

    private String createSignature(String ts, String httpMethod, String path, String body) {
        try {
            String secret = sumsubProperties.secretKey();
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKeySpec = new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(secretKeySpec);

            String dataToSign = ts + httpMethod + path + body;
            byte[] signatureBytes = mac.doFinal(dataToSign.getBytes(StandardCharsets.UTF_8));

            StringBuilder hexString = new StringBuilder();
            for (byte b : signatureBytes) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            throw new RuntimeException("Error creating signature for Sumsub.", e);
        }

    }

    public void handleWebhook(SumsubWebhookPayload body) {
        log.info("Handling webhook");
        log.info("Body: {}", body);

        String type = body.type();
        SumsubWebhookPayload.ReviewAnswer answer = body.reviewResult().reviewAnswer();
        if (!type.equals("applicantReviewed") || answer != SumsubWebhookPayload.ReviewAnswer.GREEN) {
            log.info("Webhook ignored");
            return;
        }

        String applicantId = body.applicantId();
        String timestamp = String.valueOf(Instant.now().getEpochSecond());
        String appToken = sumsubProperties.token();
        String path = APPLICANT_INFO_PATH.replace("{applicantId}", applicantId);

        String signature = createSignature(timestamp, "GET", path, "");
        Map response = restClient.get()
                .uri(path)
                .header("X-App-Token", appToken)
                .header("X-App-Access-Ts", timestamp)
                .header("X-App-Access-Sig", signature)
                .retrieve()
                .body(Map.class);

        if (response == null) {
            throw new RuntimeException("Error getting applicant info from Sumsub.");
        }

        log.info("Applicant info: {}", response);
    }
}
