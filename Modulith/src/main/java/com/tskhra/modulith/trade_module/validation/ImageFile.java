package com.tskhra.modulith.trade_module.validation;

import com.tskhra.modulith.trade_module.validation.validators.ImageFileValidator;
import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import java.lang.annotation.*;

@Documented
@Target({ElementType.PARAMETER, ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = ImageFileValidator.class)
public @interface ImageFile {
    String message() default "Invalid image file. Allowed: JPG, JPEG, PNG, WEBP.";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}