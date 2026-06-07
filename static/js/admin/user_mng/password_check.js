document.addEventListener('input', (e) => {

    if (
        e.target.id !== 'pass' &&
        e.target.id !== 'pass_check'
    ) {
        return;
    }

    const passInput = document.getElementById('pass');
    const passCheckInput = document.getElementById('pass_check');
    const passError = document.getElementById('passError');

    if (!passInput || !passCheckInput || !passError) {
        return;
    }

    const password = passInput.value.trim();
    const confirmPassword = passCheckInput.value.trim();

    if (!password || !confirmPassword) {
        passError.textContent = '';
        passError.classList.remove('success');
        return;
    }

    const matched = password === confirmPassword;

    passError.textContent = matched
        ? 'Passwords match.'
        : 'Passwords do not match.';

    passError.classList.toggle('success', matched);
});