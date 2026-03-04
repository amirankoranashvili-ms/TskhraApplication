package com.tskhra.modulith.common.exception;

import org.springframework.http.HttpStatus;
import org.springframework.modulith.NamedInterface;

@NamedInterface
public class HttpNotFoundException extends HttpException {
    public HttpNotFoundException(String message) {
        super(message, HttpStatus.NOT_FOUND);
    }
}
