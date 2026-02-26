package com.tskhra.modulith.user_module.model.responses;

import org.springframework.http.HttpStatus;

public class BadRequestErrorResponse extends ErrorResponse {
    public BadRequestErrorResponse(String message) {
        super(HttpStatus.BAD_REQUEST, message);
    }
}
