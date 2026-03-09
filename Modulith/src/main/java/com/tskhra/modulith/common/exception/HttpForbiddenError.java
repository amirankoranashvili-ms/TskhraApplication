package com.tskhra.modulith.common.exception;

import org.springframework.http.HttpStatus;

public class HttpForbiddenError extends HttpException {
    public HttpForbiddenError(String message) {
        super(message, HttpStatus.FORBIDDEN);
    }
}
