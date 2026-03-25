package com.tskhra.modulith.user_module.validation.validators;

import com.tskhra.modulith.user_module.validation.MinAge;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class MinAgeValidatorTest {

    private MinAgeValidator validator;

    @BeforeEach
    void setUp() {
        validator = new MinAgeValidator();
        MinAge annotation = mock(MinAge.class);
        when(annotation.value()).thenReturn(18);
        validator.initialize(annotation);
    }

    @Test
    void nullBirthDate_isValid() {
        assertTrue(validator.isValid(null, null));
    }

    @Test
    void exactly18YearsOld_isValid() {
        LocalDate eighteenthBirthday = LocalDate.now().minusYears(18);
        assertTrue(validator.isValid(eighteenthBirthday, null));
    }

    @Test
    void underAge_isInvalid() {
        LocalDate seventeenYearsAgo = LocalDate.now().minusYears(17);
        assertFalse(validator.isValid(seventeenYearsAgo, null));
    }

    @Test
    void overAge_isValid() {
        LocalDate thirtyYearsAgo = LocalDate.now().minusYears(30);
        assertTrue(validator.isValid(thirtyYearsAgo, null));
    }
}