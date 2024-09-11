document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    
    // Add event listener to the login form for validation
    loginForm.addEventListener('submit', function(event) {
        // Clear previous error messages
        clearErrors();

        let hasErrors = false;

        // Validate Username
        if (usernameInput.value.trim() === '') {
            showError(usernameInput, 'Username cannot be empty');
            hasErrors = true;
        }

        // Validate Password
        if (passwordInput.value.trim() === '') {
            showError(passwordInput, 'Password cannot be empty');
            hasErrors = true;
        } else if (passwordInput.value.trim().length < 6) {
            showError(passwordInput, 'Password must be at least 6 characters');
            hasErrors = true;
        }

        // Prevent form submission if there are errors
        if (hasErrors) {
            event.preventDefault();
        }
    });

    // Function to show error message
    function showError(input, message) {
        const inputGroup = input.parentElement;
        const errorElement = document.createElement('small');
        errorElement.classList.add('error-message');
        errorElement.innerText = message;
        inputGroup.appendChild(errorElement);
        input.classList.add('error');
    }

    // Function to clear all errors
    function clearErrors() {
        const errorMessages = document.querySelectorAll('.error-message');
        errorMessages.forEach(message => message.remove());

        const errorInputs = document.querySelectorAll('.error');
        errorInputs.forEach(input => input.classList.remove('error'));
    }
});
