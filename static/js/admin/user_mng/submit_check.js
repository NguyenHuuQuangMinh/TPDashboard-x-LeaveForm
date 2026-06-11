let initialized = false;

export function initSubmitCheck() {

    // Kiểm tra ngay khi form được load
    validateUserForm();

    // Tránh add event nhiều lần khi mở modal nhiều lần
    if (initialized) {
        return;
    }

    initialized = true;

    document.addEventListener('input', function (e) {

        if (!e.target.closest('#userForm')) {
            return;
        }

        validateUserForm();
    });
}


function validateUserForm() {

    const form = document.getElementById('userForm');
    const saveButton = document.getElementById('saveButton');

    if (!form || !saveButton) {
        return;
    }

    let isValid = true;


    // Kiểm tra các ô required
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {

        if (!field.value.trim()) {
            isValid = false;
        }

    });


    // Kiểm tra password
    const passInput = document.getElementById('pass');
    const passCheckInput = document.getElementById('pass_check');
    const passError = document.getElementById('passError');


    if (passInput && passCheckInput && passError) {

        const password = passInput.value.trim();
        const confirmPassword = passCheckInput.value.trim();


        // Nếu có nhập 1 trong 2 ô password thì phải khớp
        if (password || confirmPassword) {

            const matched = password === confirmPassword;


            passError.textContent = matched
                ? 'Passwords match.'
                : 'Passwords do not match.';


            passError.classList.toggle('success', matched);


            if (!matched) {
                isValid = false;
            }

        } else {

            passError.textContent = '';

            passError.classList.remove('success');
        }
    }


    // Enable/Disable nút Save
    saveButton.disabled = !isValid;
}