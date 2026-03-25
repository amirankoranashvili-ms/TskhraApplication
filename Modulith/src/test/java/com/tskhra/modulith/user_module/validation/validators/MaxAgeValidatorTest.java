package com.tskhra.modulith.user_module.validation.validators;

import com.tskhra.modulith.user_module.validation.MaxAge;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class MaxAgeValidatorTest {

    private MaxAgeValidator validator;

    @BeforeEach
    void setUp() {
        validator = new MaxAgeValidator();
        MaxAge annotation = mock(MaxAge.class);
        when(annotation.value()).thenReturn(120);
        validator.initialize(annotation);
    }

    @Test
    void nullBirthDate_isValid() {
        assertTrue(validator.isValid(null, null));
    }

    @Test
    void exactly120YearsOld_isInvalid() {
        // MaxAgeValidator uses strict less-than: age < maxAge
        LocalDate birthday120 = LocalDate.now().minusYears(120);
        assertFalse(validator.isValid(birthday120, null));
    }

    @Test
    void under120_isValid() {
        LocalDate birthday50 = LocalDate.now().minusYears(50);
        assertTrue(validator.isValid(birthday50, null));
    }

    @Test
    void over120_isInvalid() {
        LocalDate birthday130 = LocalDate.now().minusYears(130);
        assertFalse(validator.isValid(birthday130, null));
    }
}