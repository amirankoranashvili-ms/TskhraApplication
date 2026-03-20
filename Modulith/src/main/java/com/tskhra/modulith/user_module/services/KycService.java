package com.tskhra.modulith.user_module.services;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tskhra.modulith.common.properties.SumsubProperties;
import com.tskhra.modulith.user_module.model.requests.SubsubWebhookPayload;
import com.tskhra.modulith.user_module.model.responses.KycTokenResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestTemplate;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;

@Service
@Slf4j
public class KycService {

    private final SumsubProperties sumsubProperties;
    private final RestClient restClient;
    private final UserService userService;

    private static final String URI_PATH = "/resources/accessTokens/sdk";


    public KycService(SumsubProperties sumsubProperties, RestClient.Builder restClientBuilder, UserService userService) {
        this.sumsubProperties = sumsubProperties;
        this.restClient = restClientBuilder.baseUrl(sumsubProperties.baseUrl())
                .build();
        this.userService = userService;
    }


    public KycTokenResponse getAccessToken(Jwt jwt) {
//        String userId = userService.getCurrentUser(jwt).getId().toString();
//        String userId = UUID.randomUUID().toString();
        String  userId = jwt.getClaimAsString("sub");
        log.info("User idd: {}", userId);
        String timestamp = String.valueOf(Instant.now().getEpochSecond());
        log.info("Timestamp: {}", timestamp);
        String levelName = sumsubProperties.levelName();
        String appToken = sumsubProperties.token();

        String jsonBody = """
                {
                  "userId": "%s",
                  "levelName": "%s",
                  "ttlInSecs": 600
                }
                """.formatted(userId, levelName).trim();

        log.info("Json body: {}", jsonBody);

        String signature = createSignature(timestamp, jsonBody);
        log.info("Signature: {}", signature);

        Map response = restClient.post()
                .uri(URI_PATH)
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

    private String createSignature(String ts, String body){
        try {
            String secret = sumsubProperties.secretKey();
            String path = URI_PATH;
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKeySpec = new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(secretKeySpec);
            String httpMethod = "POST";

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

    public void handleWebhook(SubsubWebhookPayload body) {
        log.info("Handling webhook");
        log.info("Body: {}", body);
    }
}
