package com.tskhra.modulith.common.exception.http_exceptions;

import org.springframework.http.HttpStatus;
import org.springframework.modulith.NamedInterface;

@NamedInterface
public class HttpBadRequestException extends HttpException {
    public HttpBadRequestException(String message) {
        super(message, HttpStatus.BAD_REQUEST);
    }
}
