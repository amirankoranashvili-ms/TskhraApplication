package com.tskhra.modulith.common.exception.custom_status_exceptions;

import com.tskhra.modulith.common.model.enums.MyCustomStatus;
import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.modulith.NamedInterface;

@Getter
@NamedInterface
public class CustomStatusException extends RuntimeException {

    private final int customStatusCode;
    private final HttpStatus httpStatus;

    public CustomStatusException(MyCustomStatus myCustomStatus) {
        super(myCustomStatus.description());
        this.customStatusCode = myCustomStatus.value();
        this.httpStatus = myCustomStatus.httpStatus();
    }

    public CustomStatusException(MyCustomStatus myCustomStatus, String message) {
        super(message);
        this.customStatusCode = myCustomStatus.value();
        this.httpStatus = myCustomStatus.httpStatus();
    }

}
