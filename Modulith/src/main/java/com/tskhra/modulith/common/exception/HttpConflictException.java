package com.tskhra.modulith.common.exception;

import org.springframework.http.HttpStatus;
import org.springframework.modulith.NamedInterface;

@NamedInterface
public class HttpConflictException extends HttpException {
    public HttpConflictException(String message) {
        super(message, HttpStatus.CONFLICT);

    }
}
