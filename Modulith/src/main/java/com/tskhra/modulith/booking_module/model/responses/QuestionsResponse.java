package com.tskhra.modulith.booking_module.model.responses;

import java.util.List;

public record QuestionsResponse(
        String category,
        List<String> questions
) {
}
