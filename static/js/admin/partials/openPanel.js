import { initModuleFeatures }
    from './crudModules.js';

export async function openCrud(module = null, id = null, title = '',url = null, feature = null) {

    const crudOverlay = document.getElementById('crudOverlay');
    const crudContent = document.getElementById('crudContent');
    const crudTitle = document.getElementById('crudTitle');
    const crudLoading = document.getElementById('crudLoading');

    try {
        crudOverlay.classList.add('active');

        crudLoading.style.display = 'flex';
        crudContent.style.display = 'none';

        crudTitle.textContent = title || `${module}`;
        const fetchUrl = url || `/partial/${module}/${id}`;
        const response = await fetch(fetchUrl);
        const html = await response.text();
        crudContent.innerHTML = html;

        const initName = feature || module;
        if (initName) {
            await initModuleFeatures(initName);
        }

    } catch (err) {

        crudContent.innerHTML =
            '<div class="error">Failed to load data.</div>';

    } finally {

        crudLoading.style.display = 'none';
        crudContent.style.display = 'block';
    }
}