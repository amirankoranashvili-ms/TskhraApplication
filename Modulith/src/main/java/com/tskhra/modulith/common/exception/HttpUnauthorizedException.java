package com.tskhra.modulith.common.exception;

import org.springframework.http.HttpStatus;

public class HttpUnauthorizedException extends HttpException {
    public HttpUnauthorizedException(String message) {
        super(message, HttpStatus.UNAUTHORIZED);
    }
}
