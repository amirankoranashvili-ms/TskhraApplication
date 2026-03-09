package com.tskhra.modulith.booking_module.validation.validators;

import com.tskhra.modulith.booking_module.model.embeddable.WeekTimeInterval;
import com.tskhra.modulith.booking_module.validation.ValidTimeInterval;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

public class TimeIntervalValidator implements ConstraintValidator<ValidTimeInterval, WeekTimeInterval> {

    @Override
    public boolean isValid(WeekTimeInterval interval, ConstraintValidatorContext context) {
        if (interval == null) {
            return true;
        }
        return interval.getStartTime() < interval.getEndTime();
    }

}
