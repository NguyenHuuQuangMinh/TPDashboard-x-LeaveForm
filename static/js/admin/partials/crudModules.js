export async function initModuleFeatures(module) {

    const modules = {

        routes: async () => {

            const m =
                await import('../routes/iconChange.js');

            m.initIconPreview();
        },
        users: async () => {

            const m =
                await import('../user_mng/auto_field.js');

            m.initAutoField();
        },
        permissions: async () => {

            const m =
                await import(
                    '../roles_permission/permission.js'
                );

            m.initPermissionForm();
        }
    };

    if (modules[module]) {
        await modules[module]();
    }
}