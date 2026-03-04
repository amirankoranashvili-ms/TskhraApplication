package com.tskhra.modulith.common.exception;

import org.springframework.http.HttpStatus;
import org.springframework.modulith.NamedInterface;

@NamedInterface
public class HttpUnauthorizedException extends HttpException {
    public HttpUnauthorizedException(String message) {
        super(message, HttpStatus.UNAUTHORIZED);
    }
}
