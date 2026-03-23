package com.tskhra.modulith.common.model.enums;

import jakarta.annotation.Nullable;
import org.springframework.http.HttpStatus;
import org.springframework.modulith.NamedInterface;

@NamedInterface
public enum MyCustomStatus {
    BUSINESS_NUMBER_LIMIT_REACHED(1000, HttpStatus.BAD_REQUEST, "User cannot create any more businesses.");

    private static final MyCustomStatus[] VALUES = values();
    private final int value;
    private final HttpStatus httpStatus;
    private final String description;

    private MyCustomStatus(int value, HttpStatus httpStatus, String description) {
        this.value = value;
        this.httpStatus = httpStatus;
        this.description = description;
    }

    public int value() {
        return this.value;
    }

    public HttpStatus httpStatus() {
        return this.httpStatus;
    }

    public String description() {
        return this.description;
    }

    @Override
    public String toString() {
        return this.value + " - " + this.description;
    }

    public static MyCustomStatus valueOf(int statusCode) {
        MyCustomStatus status = resolve(statusCode);
        if (status == null) {
            throw new IllegalArgumentException("Invalid status code: " + statusCode);
        }
        return status;
    }

    public static @Nullable MyCustomStatus resolve(int statusCode) {
        for (MyCustomStatus status : VALUES) {
            if (status.value == statusCode) {
                return status;
            }
        }
        return null;
    }

}
