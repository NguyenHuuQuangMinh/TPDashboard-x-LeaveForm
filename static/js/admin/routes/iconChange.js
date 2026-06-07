export async function initIconPreview() {

    const routeIcon =
        document.getElementById('routeIcon');

    const iconPreview =
        document.getElementById('iconPreview');

    if (!routeIcon || !iconPreview) {
        return;
    }

    routeIcon.addEventListener('input', () => {

        iconPreview.className =
            routeIcon.value.trim();

    });

}