package com.tskhra.modulith.user_module.validation;

import com.tskhra.modulith.user_module.validation.validators.MaxAgeValidator;
import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

@Documented
@Constraint(validatedBy = MaxAgeValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
public @interface MaxAge {
    String message() default "Too old!";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};

    int value();
}
