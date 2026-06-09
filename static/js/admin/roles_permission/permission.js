export function initPermissionForm() {

    const form =
        document.getElementById(
            "permissionForm"
        );

    if (!form) return;

    form.addEventListener(
    "submit",
    async (e) => {

        e.preventDefault();

        const fd = new FormData(form);

        try {

            const res = await fetch(
                "/permissions/save",
                {
                    method: "POST",
                    body: fd
                }
            );

            const json = await res.json();

            if (json.ok) {

                showToast(
                    json.message,
                    "success"
                );

            } else {

                showToast(
                    json.error,
                    "error"
                );

            }

        } catch (err) {

            showToast(
                "System error.",
                "error"
            );

        }
    }
);
}