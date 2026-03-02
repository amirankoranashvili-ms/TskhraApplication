package com.tskhra.modulith.user_module.validation;

import com.tskhra.modulith.user_module.validation.validators.MinAgeValidator;
import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

@Documented
@Constraint(validatedBy = MinAgeValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
public @interface MinAge {
    String message() default "Does not meet minimum age requirement";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};

    int value();
}
