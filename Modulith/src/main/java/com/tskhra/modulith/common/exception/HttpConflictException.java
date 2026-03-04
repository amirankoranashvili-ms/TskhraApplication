package com.tskhra.modulith.common.exception;

import org.springframework.http.HttpStatus;

public class HttpConflictException extends HttpException {
    public HttpConflictException(String message) {
        super(message, HttpStatus.CONFLICT);

    }
}
