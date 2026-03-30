package com.tskhra.modulith.booking_module.validation.validators;

import com.tskhra.modulith.booking_module.model.embeddable.WeekTimeInterval;
import com.tskhra.modulith.booking_module.model.requests.BusinessRegistrationDto;
import com.tskhra.modulith.booking_module.validation.ValidRestTimes;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.util.List;
import java.util.Objects;

public class RestTimesValidator implements ConstraintValidator<ValidRestTimes, BusinessRegistrationDto> {

    @Override
    public boolean isValid(BusinessRegistrationDto dto, ConstraintValidatorContext context) {
        if (dto.restTimes() == null || dto.restTimes().isEmpty()) {
            return true;
        }
        if (dto.workTimes() == null || dto.workTimes().isEmpty()) {
            return false;
        }

        for (WeekTimeInterval rest : dto.restTimes()) {
            if (rest == null) {
                continue;
            }
            if (!isWithinAnyWorkTime(rest, dto.workTimes())) {
                return false;
            }
        }
        return true;
    }

    private boolean isWithinAnyWorkTime(WeekTimeInterval rest, List<WeekTimeInterval> workTimes) {
        return workTimes.stream()
                .filter(Objects::nonNull)
                .filter(work -> work.getWeekDay() == rest.getWeekDay())
                .anyMatch(work -> rest.getStartTime() >= work.getStartTime()
                        && rest.getEndTime() <= work.getEndTime());
    }

}
