package com.tskhra.modulith.booking_module.validation;

import com.tskhra.modulith.booking_module.validation.validators.TimeIntervalValidator;
import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = TimeIntervalValidator.class)
@Documented
public @interface ValidTimeInterval {

    String message() default "startTime must be less than endTime";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};

}
