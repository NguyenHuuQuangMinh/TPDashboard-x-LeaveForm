export function initAutoField() {

    const roleSelect = document.getElementById('roleSelect');
    const departmentSelect = document.getElementById('departmentSelect');

    const jobTitleInput = document.getElementById('jobTitle');
    const reportToInput = document.getElementById('reportTo');

    if (
        !roleSelect ||
        !departmentSelect ||
        !jobTitleInput ||
        !reportToInput
    ) {
        return;
    }

    function updateFields() {

        const roleName =
            roleSelect.options[
                roleSelect.selectedIndex
            ]?.text || '';

        const departmentName =
            departmentSelect.options[
                departmentSelect.selectedIndex
            ]?.text || '';

        jobTitleInput.value = departmentName;

        reportToInput.value =
            `${departmentName} ${roleName}`.trim();
    }

    roleSelect.addEventListener('change', updateFields);
    departmentSelect.addEventListener('change', updateFields);

    updateFields();
}