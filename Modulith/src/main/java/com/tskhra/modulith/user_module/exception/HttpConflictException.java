package com.tskhra.modulith.user_module.exception;

import org.springframework.http.HttpStatus;

public class HttpConflictException extends HttpException {
    public HttpConflictException(String message) {
        super(message, HttpStatus.CONFLICT);

    }
}
