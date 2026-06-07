document.addEventListener("DOMContentLoaded", () => {
    const overlay = document.querySelector(".toast-overlay");
    if (!overlay) return;

    setTimeout(() => {
        overlay.remove();
    }, 2200);
});

export function showToast(
    message,
    category = 'success'
) {

    const overlay =
        document.createElement('div');

    overlay.className =
        'toast-overlay';

    overlay.innerHTML = `
        <div class="toast ${category}">
            ${message}
        </div>
    `;

    document.body.appendChild(
        overlay
    );

    setTimeout(() => {

        overlay.remove();

    }, 2200);

}
