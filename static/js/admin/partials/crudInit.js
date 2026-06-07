import { openCrud }
    from './openPanel.js';

export function initCrud() {

    document.addEventListener(
        'click',
        e => {

            const trigger =
                e.target.closest(
                    '[data-crud-open]'
                );

            if (!trigger) return;

            openCrud(
                trigger.dataset.module,
                trigger.dataset.id,
                trigger.dataset.title
            );
        }
    );

}