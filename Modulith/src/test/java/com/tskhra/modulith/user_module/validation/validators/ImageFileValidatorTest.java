package com.tskhra.modulith.user_module.validation.validators;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockMultipartFile;

import static org.junit.jupiter.api.Assertions.*;

class ImageFileValidatorTest {

    private ImageFileValidator validator;

    @BeforeEach
    void setUp() {
        validator = new ImageFileValidator();
    }

    @Test
    void nullFile_isInvalid() {
        assertFalse(validator.isValid(null, null));
    }

    @Test
    void emptyFile_isInvalid() {
        MockMultipartFile file = new MockMultipartFile("file", "photo.png", "image/png", new byte[0]);
        assertFalse(validator.isValid(file, null));
    }

    @Test
    void validJpegFile_isValid() {
        MockMultipartFile file = new MockMultipartFile("file", "photo.jpg", "image/jpeg", new byte[]{1, 2, 3});
        assertTrue(validator.isValid(file, null));
    }

    @Test
    void validPngFile_isValid() {
        MockMultipartFile file = new MockMultipartFile("file", "photo.png", "image/png", new byte[]{1, 2, 3});
        assertTrue(validator.isValid(file, null));
    }

    @Test
    void disallowedContentType_isInvalid() {
        MockMultipartFile file = new MockMultipartFile("file", "doc.pdf", "application/pdf", new byte[]{1, 2, 3});
        assertFalse(validator.isValid(file, null));
    }

    @Test
    void disallowedExtension_isInvalid() {
        // Valid content type but wrong extension
        MockMultipartFile file = new MockMultipartFile("file", "photo.gif", "image/png", new byte[]{1, 2, 3});
        assertFalse(validator.isValid(file, null));
    }

    @Test
    void noExtension_isInvalid() {
        MockMultipartFile file = new MockMultipartFile("file", "photo", "image/png", new byte[]{1, 2, 3});
        assertFalse(validator.isValid(file, null));
    }
}