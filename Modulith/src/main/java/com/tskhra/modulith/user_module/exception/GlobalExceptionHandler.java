package com.tskhra.modulith.user_module.exception;

import com.tskhra.modulith.user_module.model.responses.BadRequestErrorResponse;
import com.tskhra.modulith.user_module.model.responses.ConflictErrorResponse;
import com.tskhra.modulith.user_module.model.responses.ErrorResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.List;
import java.util.stream.Collectors;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(UserAlreadyExistsException.class)
    public ResponseEntity<ErrorResponse> handleUserAlreadyExists(UserAlreadyExistsException ex) {
        ErrorResponse response = new ConflictErrorResponse(ex.getMessage());
        return new ResponseEntity<>(response, response.getStatus());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleMethodArgumentNotValid(MethodArgumentNotValidException ex) {
        List<String> errors = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .toList();

        ErrorResponse response = new BadRequestErrorResponse(errors.toString());
        return new ResponseEntity<>(response, response.getStatus());
    }

}
