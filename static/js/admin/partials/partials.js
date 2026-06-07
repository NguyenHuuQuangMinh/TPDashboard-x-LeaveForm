import { initCrud }
    from './crudInit.js';

import { initCrudClose }
    from './crudClose.js';

document.addEventListener(
    'DOMContentLoaded',
    () => {
        initCrud();
        initCrudClose();
    }
);