package com.tskhra.modulith.user_module.exception;

import org.springframework.http.HttpStatus;

public class HttpBadRequestException extends HttpException {
    public HttpBadRequestException(String message) {
        super(message, HttpStatus.BAD_REQUEST);
    }
}
