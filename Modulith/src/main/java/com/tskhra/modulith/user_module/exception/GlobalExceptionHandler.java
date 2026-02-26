package com.tskhra.modulith.user_module.exception;

import com.tskhra.modulith.user_module.model.responses.ConflictErrorResponse;
import com.tskhra.modulith.user_module.model.responses.ErrorResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(UserAlreadyExistsException.class)
    public ResponseEntity<ErrorResponse> handleUserAlreadyExists(UserAlreadyExistsException ex) {
        ErrorResponse response = new ConflictErrorResponse(ex.getMessage());
        return new ResponseEntity<>(response, response.getStatus());
    }

}
