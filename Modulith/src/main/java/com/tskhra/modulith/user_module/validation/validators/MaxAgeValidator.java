package com.tskhra.modulith.user_module.validation.validators;

import com.tskhra.modulith.user_module.validation.MaxAge;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.time.LocalDate;
import java.time.Period;

public class MaxAgeValidator implements ConstraintValidator<MaxAge, LocalDate> {

    private int maxAge;

    @Override
    public void initialize(MaxAge constraintAnnotation) {
        this.maxAge = constraintAnnotation.value();
    }

    @Override
    public boolean isValid(LocalDate birthDate, ConstraintValidatorContext context) {
        if (birthDate == null) {
            return true;
        }

        int age = Period.between(birthDate, LocalDate.now()).getYears();
        return age >= maxAge;
    }

}
