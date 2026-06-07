let currentDetailConfig = null;
export async function openRevenueDetail({

    title,
    api = null,
    data = null,
    quarter = null,
    year = null,
    month = null,
    params = {},

    columns = [],

    groupBy = [],

    formatters = {}

}) {
    const modal =
        document.getElementById('detailModal');

    const titleEl =
        document.getElementById('detailTitle');

    const headEl =
        document.getElementById('detailHead');

    const bodyEl =
        document.getElementById('detailBody');

    titleEl.textContent = title;

    currentDetailConfig = {
        title,
        api,
        data,
        quarter,
        year,
        month,
        params,
        columns,
        groupBy,
        formatters
    };
    const fromDate =
    document.getElementById('detailFromDate')?.value;

    const toDate =
        document.getElementById('detailToDate')?.value;
    const fromInput =
        document.getElementById('detailFromDate');

    const toInput =
        document.getElementById('detailToDate');
    const minYear =
        year || 2025;

    const maxYear =
        year || 2027;

    if (quarter) {

        const quarterRanges = {

            Q1: {
                min: `${minYear}-01-01`,
                max: `${maxYear}-03-31`
            },

            Q2: {
                min: `${minYear}-04-01`,
                max: `${maxYear}-06-30`
            },

            Q3: {
                min: `${minYear}-07-01`,
                max: `${maxYear}-09-30`
            },

            Q4: {
                min: `${minYear}-10-01`,
                max: `${maxYear}-12-31`
            }
        };

        const range =
            quarterRanges[quarter];

        if (range) {

            fromInput.min = range.min;
            fromInput.max = range.max;

            toInput.min = range.min;
            toInput.max = range.max;
        }
    }

    if(month){

            const start =
                `${minYear}-${String(month).padStart(2, '0')}-01`;

            const endDate =
                new Date(maxYear, month, 0);

            const end =
                `${maxYear}-${String(month).padStart(2, '0')}-${String(endDate.getDate()).padStart(2, '0')}`;

            fromInput.min = start;
            fromInput.max = end;

            toInput.min = start;
            toInput.max = end;

            if (!fromInput.value) {
                fromInput.value = start;
            }

            if (!toInput.value) {
                toInput.value = end;
            }
        }

    if(!quarter && !month){
        fromInput.min =
        `${minYear}-01-01`;

        fromInput.max =
            `${maxYear}-12-31`;

        toInput.min =
            `${minYear}-01-01`;

        toInput.max =
            `${maxYear}-12-31`;
    }

    const finalParams = {
        ...params
    };

    if (fromDate) {
        finalParams.from_date = fromDate;
    }

    if (toDate) {
        finalParams.to_date = toDate;
    }
    let finalData = data;
    if (finalData) {

        finalData = finalData.filter(row => {

            const rowDate =
                new Date(row.service_date);

            // ===== FROM DATE =====

            if (fromDate) {

                const from =
                    new Date(fromDate);

                if (rowDate < from) {
                    return false;
                }
            }

            // ===== TO DATE =====

            if (toDate) {

                const to =
                    new Date(toDate);

                if (rowDate > to) {
                    return false;
                }
            }

            return true;
        });
    }
    if(!finalData && api){
        const query =
        new URLSearchParams(finalParams);

        const response =
        await fetch(
            `${api}?${query.toString()}`
        );

        if (!response.ok) {

            const text =
                await response.text();

            console.error(text);

            alert('Server Error');

            return;
        }
        finalData =
        await response.json();
    }

    if (!finalData.length) {

        headEl.innerHTML = '';

        bodyEl.innerHTML = `
            <tr>
                <td>No data</td>
            </tr>
        `;

        modal.classList.add('show');

        return;
    }

    if (!columns.length) {

        columns =
            Object.keys(finalData[0]).map(key => ({
                key,
                label: key
            }));
    }

    headEl.innerHTML = '';

    let html = '';

    let currentYear = null;
    let currentMonth = null;

    finalData.forEach(row => {

        // ===== YEAR =====
        if (row.year !== currentYear) {

            currentYear = row.year;

            currentMonth = null;

            html += `
                <tr class="year-row">
                    <td colspan="${columns.length}">
                        Year : ${currentYear}
                    </td>
                </tr>
            `;
        }

        // ===== MONTH =====
        if (row.month !== currentMonth) {

            currentMonth = row.month;

            html += `
                <tr class="month-row">
                    <td colspan="${columns.length}">
                        Month : ${currentMonth}
                    </td>
                </tr>
            `;

            // ===== HEADER =====
            html += `
                <tr class="detail-header-row">

                    ${columns.map(col => `
                        <th>${col.label}</th>
                    `).join('')}

                </tr>
            `;
        }

        html += `
            <tr>

                ${columns.map(col => {

                    let value =
                        row[col.key];

                    // ===== FORMAT DATE =====
                    if (
                        col.key === 'service_date'
                        && value
                    ) {

                        const d =
                            new Date(value);

                        value =
                            String(d.getDate())
                                .padStart(2, '0')
                            + '/'
                            + String(d.getMonth() + 1)
                                .padStart(2, '0')
                            + '/'
                            + d.getFullYear();
                    }

                    // ===== CUSTOM FORMAT =====
                    if (
                        formatters[col.key]
                    ) {

                        value =
                            formatters[col.key](value, row);
                    }

                    return `
                        <td>${value ?? ''}</td>
                    `;

                }).join('')}

            </tr>
        `;
    });

    bodyEl.innerHTML = html;

    modal.classList.add('show');
}

document
    .getElementById('detailFilterBtn')
    ?.addEventListener('click', async () => {

        if (!currentDetailConfig) return;

        await openRevenueDetail(currentDetailConfig);
    });

document
    .getElementById('closeDetailModal')
    ?.addEventListener('click', () => {

        document
            .getElementById('detailModal')
            .classList.remove('show');
    });