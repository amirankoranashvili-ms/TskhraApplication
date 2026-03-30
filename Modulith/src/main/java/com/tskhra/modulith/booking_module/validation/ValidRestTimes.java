package com.tskhra.modulith.booking_module.validation;

import com.tskhra.modulith.booking_module.validation.validators.RestTimesValidator;
import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = RestTimesValidator.class)
@Documented
public @interface ValidRestTimes {

    String message() default "Rest times must be within working times";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};

}
