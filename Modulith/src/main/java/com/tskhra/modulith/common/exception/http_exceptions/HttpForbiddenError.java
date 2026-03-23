package com.tskhra.modulith.common.exception.http_exceptions;

import org.springframework.http.HttpStatus;
import org.springframework.modulith.NamedInterface;

@NamedInterface
public class HttpForbiddenError extends HttpException {
    public HttpForbiddenError(String message) {
        super(message, HttpStatus.FORBIDDEN);
    }
}
