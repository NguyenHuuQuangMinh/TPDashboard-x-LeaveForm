export function initCrudClose() {

    document.addEventListener(
        'click',
        (e) => {

            const btn =
                e.target.closest('[data-crud-close]');

            if (!btn) return;

            btn
                .closest('.close-crud')
                ?.classList.remove('active');

        }
    );

}