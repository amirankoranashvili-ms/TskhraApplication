package com.tskhra.modulith.user_module.model.responses;

import org.springframework.http.HttpStatus;

public class ConflictErrorResponse extends ErrorResponse {
    public ConflictErrorResponse(String message) {
        super(HttpStatus.CONFLICT, message);
    }
}
