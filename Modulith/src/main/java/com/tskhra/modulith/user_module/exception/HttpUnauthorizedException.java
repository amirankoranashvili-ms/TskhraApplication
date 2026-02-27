package com.tskhra.modulith.user_module.exception;

import org.springframework.http.HttpStatus;

public class HttpUnauthorizedException extends HttpException {
    public HttpUnauthorizedException(String message) {
        super(message, HttpStatus.UNAUTHORIZED);
    }
}
