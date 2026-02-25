document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");

    const username = document.getElementById("username");
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    // Добавляем поле подтверждения пароля
    const passwordConfirm = document.getElementById("password-confirm");

    // 1. Находим кнопку отправки формы
    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');

    // 2. Изначально делаем кнопку неактивной
    if (submitBtn) {
        submitBtn.disabled = true;
    }


    const showError = (input, message) => {
        let container = input.parentElement;
        if (container.classList.contains('pf-c-input-group') || container.hasAttribute('dir')) {
            container = container.parentElement;
        }

        let error = container.querySelector(".error-message");

        if (!error) {
            error = document.createElement("div");
            error.className = "error-message";
            container.appendChild(error);
        }

        error.textContent = message;
        input.classList.add("input-error");
    };

    const clearError = (input) => {
        let container = input.parentElement;
        if (container.classList.contains('pf-c-input-group') || container.hasAttribute('dir')) {
            container = container.parentElement;
        }

        const error = container.querySelector(".error-message");
        if (error) {
            error.textContent = "";
        }
        input.classList.remove("input-error");
    };



    // USERNAME VALIDATION
    const validateUsername = (silent = false) => {
        if (!username) return true;

        const rawValue = username.value;
        const value = rawValue.trim();


        if (/\s/.test(rawValue)) {
            if (!silent) showError(username, "No spaces allowed");
            return false;
        }


        if (value.length === 0) {
            if (!silent) showError(username, "Username is required");
            return false;
        }
        if (value.length < 3) {
            if (!silent) showError(username, "Minimum 3 characters");
            return false;
        }
        if (value.length > 50) {
            if (!silent) showError(username, "Maximum 50 characters");
            return false;
        }
        if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            if (!silent) showError(username, "Only latin letters, numbers and underscore");
            return false;
        }
        if (!/[a-zA-Z]/.test(value)) {
            if (!silent) showError(username, "Must contain at least one letter");
            return false;
        }

        if (/__+/.test(value)) {
            if (!silent) showError(username, "Consecutive underscores are not allowed");
            return false;
        }

        if (!silent) clearError(username);
        return true;
    };

    // EMAIL VALIDATION
    const validateEmail = (silent = false) => {
        if (!email) return true;
        const value = email.value;
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!regex.test(value)) {
            if (!silent) showError(email, "Invalid email address");
            return false;
        }

        if (!silent) clearError(email);
        return true;
    };

    // PASSWORD VALIDATION
    const validatePassword = (silent = false) => {
        if (!password) return true;
        const value = password.value;

        if (value.length < 8) {
            if (!silent) showError(password, "Minimum 8 characters");
            return false;
        }
        if (/\s/.test(value)) {
            if (!silent) showError(password, "No spaces allowed");
            return false;
        }
        if (!/[A-Z]/.test(value)) {
            if (!silent) showError(password, "Add one uppercase letter");
            return false;
        }
        if (!/[a-z]/.test(value)) {
            if (!silent) showError(password, "Add one lowercase letter");
            return false;
        }
        if (!/\d/.test(value)) {
            if (!silent) showError(password, "Add at least one number");
            return false;
        }
        if (!/[!@#$%^&*(),.?":{}|<>_-]/.test(value)) {
            if (!silent) showError(password, "Add one special character");
            return false;
        }

        if (!silent) clearError(password);
        return true;
    };

    // PASSWORD CONFIRM VALIDATION
    const validatePasswordConfirm = (silent = false) => {
        if (!passwordConfirm) return true;

        const value = passwordConfirm.value;
        const originalPassword = password.value;

        if (value.length === 0) {
            if (!silent) showError(passwordConfirm, "Please confirm your password");
            return false;
        }

        if (value !== originalPassword) {
            if (!silent) showError(passwordConfirm, "Passwords do not match");
            return false;
        }

        if (!silent) clearError(passwordConfirm);
        return true;
    };


    // --- ACTIVATE BTN LOGIC ---


    const toggleSubmitButton = () => {
        if (!submitBtn) return;

        const isValid =
            validateUsername(true) &&
            validateEmail(true) &&
            validatePassword(true) &&
            validatePasswordConfirm(true);

        submitBtn.disabled = !isValid;
    };


    // REALTIME EVENTS
    if (username) {
        username.addEventListener("input", () => {
            validateUsername();
            toggleSubmitButton();
        });
    }

    if (email) {
        email.addEventListener("input", () => {
            validateEmail();
            toggleSubmitButton();
        });
    }

    if (password) {
        password.addEventListener("input", () => {
            validatePassword();
            // Если пользователь меняет первый пароль, нужно заново проверить второй
            if (passwordConfirm && passwordConfirm.value.length > 0) {
                validatePasswordConfirm();
            }
            toggleSubmitButton();
        });
    }

    if (passwordConfirm) {
        passwordConfirm.addEventListener("input", () => {
            validatePasswordConfirm();
            toggleSubmitButton();
        });
    }

    toggleSubmitButton();


    // FINAL CHECK BEFORE SUBMIT
    form.addEventListener("submit", (e) => {
        const valid =
            validateUsername() &&
            validateEmail() &&
            validatePassword() &&
            validatePasswordConfirm();

        if (!valid) e.preventDefault();
    });
});