package com.tskhra.modulith.user_module.model.responses;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public record SumsubApplicantResponse(
        String id,
        String externalUserId,
        FixedInfo fixedInfo,
        String phone,
        List<Metadata> metadata
) {

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record FixedInfo(
            String firstName,
            String lastName,
            String dob,
            String gender
    ) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Metadata(
            String key,
            String value
    ) {}
}
