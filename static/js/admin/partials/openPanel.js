import { initModuleFeatures }
    from './crudModules.js';

export async function openCrud(module, id, title = '') {

    const crudOverlay = document.getElementById('crudOverlay');
    const crudContent = document.getElementById('crudContent');
    const crudTitle = document.getElementById('crudTitle');
    const crudLoading = document.getElementById('crudLoading');

    try {
        crudOverlay.classList.add('active');

        crudLoading.style.display = 'flex';
        crudContent.style.display = 'none';

        crudTitle.textContent = title || `${module}`;

        const response = await fetch(`/partial/${module}/${id}`);
        const html = await response.text();

        crudContent.innerHTML = html;

        await initModuleFeatures(module);

    } catch (err) {

        crudContent.innerHTML =
            '<div class="error">Failed to load data.</div>';

    } finally {

        crudLoading.style.display = 'none';
        crudContent.style.display = 'block';
    }
}