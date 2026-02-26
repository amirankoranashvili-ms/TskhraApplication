package com.tskhra.modulith.user_module.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public class HttpException extends RuntimeException {

    private HttpStatus status;
    public HttpException(String message, HttpStatus status) {
        super(message);
        this.status = status;
    }
}
