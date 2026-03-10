package com.tskhra.modulith.common.exception;

import jdk.jfr.Name;
import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.modulith.NamedInterface;

@Getter
@NamedInterface
public class HttpException extends RuntimeException {

    private final HttpStatus status;
    public HttpException(String message, HttpStatus status) {
        super(message);
        this.status = status;
    }
}
