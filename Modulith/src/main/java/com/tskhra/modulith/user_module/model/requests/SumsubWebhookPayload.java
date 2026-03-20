package com.tskhra.modulith.user_module.model.requests;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.time.OffsetDateTime;

@JsonIgnoreProperties(ignoreUnknown = true)
public record SumsubWebhookPayload(
        String applicantId,
        String inspectionId,
        ApplicantType applicantType,
        String correlationId,
        String levelName,
        boolean sandboxMode,
        String externalUserId,
        String type,
        ReviewResult reviewResult,
        ReviewStatus reviewStatus,

        @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd HH:mm:ssZ")
        OffsetDateTime createdAt,
        String clientId
) {
    public record ReviewResult(ReviewAnswer reviewAnswer) {}

    public enum ApplicantType { individual, company }
    public enum ReviewStatus { completed, pending, init }
    public enum ReviewAnswer { GREEN, RED }
}
