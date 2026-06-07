import { openRevenueDetail }
from './detail-modal.js';

let quarterChart = null;
let revenueQuarterDetailCache = [];

export async function loadQuarterChart() {
    const loadingEl =
    document.getElementById('detailLoading');
    const year =
        document.getElementById('chartYearFilter')?.value;

    const params =
        new URLSearchParams(window.location.search);

    if (year) {
        params.set('year', year);
    } else {
        params.delete('year');
    }
    loadingEl.style.display = 'flex';
    try {
    const response =
        await fetch(
            `/admin/chart/revenue-quarter?${params.toString()}`
        );
    const data = await response.json();
    const totals = {
        Q1: 0,
        Q2: 0,
        Q3: 0,
        Q4: 0
    };

    data.forEach(r => {
        totals[r.quarter] += Number(r.revenue);
    });

    const ctx =
        document.getElementById('quarterPieChart');

    if (!ctx) return;

    if (quarterChart) {
        quarterChart.destroy();
    }

    quarterChart = new Chart(ctx, {

        type: 'pie',

        data: {
            labels: [
                'Quarter 1',
                'Quarter 2',
                'Quarter 3',
                'Quarter 4'
            ],

            datasets: [{
                data: [
                    totals.Q1,
                    totals.Q2,
                    totals.Q3,
                    totals.Q4
                ],

                backgroundColor: [
                    '#B08D4A',
                    '#D4A96A',
                    '#8C6A3B',
                    '#E6C28B'
                ],

                borderWidth: 2,
                borderColor: '#fff'
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            onClick: async (evt, elements) => {
                if(!elements.length) return;

                const index = elements[0].index;

                const quarterMap = [
                    'Q1',
                    'Q2',
                    'Q3',
                    'Q4'
                ];

                const quarter = quarterMap[index];
                const cacheKey =
                    `${quarter}_${year || 'all'}_${params.toString()}`;
                let detailData =
    revenueQuarterDetailCache[cacheKey];

// ===== FETCH FIRST TIME =====

    if (!detailData) {

        const detailParams =
            new URLSearchParams({
                quarter,
                ...Object.fromEntries(params.entries())
            });

        const response =
            await fetch(
                `/admin/chart/revenue-quarter-detail?${detailParams.toString()}`
            );

        detailData =
            await response.json();

        // cache
        revenueQuarterDetailCache[cacheKey] =
            detailData;
        }

    await openRevenueDetail({

        title: `Revenue Detail - ${quarter}`,
        quarter,
        year,
        data: detailData,

        groupBy: [
            'year',
            'month'
        ],

        columns: [

            {
                key: 'service_date',
                label: 'Date'
            },

            {
                key: 'agent_code',
                label: 'Code'
            },

            {
                key: 'agent_name',
                label: 'Agent'
            },

            {
                key: 'revenue',
                label: 'Revenue'
            }
        ],

        formatters: {

            revenue: value =>
                Number(value)
                    .toLocaleString('en-US')
            }
        });
            },
            plugins: {

                legend: {
                    position: 'bottom'
                },

                tooltip: {
                    callbacks: {

                        label: function(context) {

                            const value = context.raw;

                            const total =
                                context.dataset.data.reduce(
                                    (a, b) => a + b,
                                    0
                                );

                            const percent =
                                (
                                    (value / total) * 100
                                ).toFixed(1);

                            const quarterInfo = {

                                'Quarter 1': 'Jan - Mar',
                                'Quarter 2': 'Apr - Jun',
                                'Quarter 3': 'Jul - Sep',
                                'Quarter 4': 'Oct - Dec'
                            };

                            return [
                                `${context.label} (${quarterInfo[context.label]})`,
                                `${value.toLocaleString('en-US')} USD`,
                                `${percent}% of total revenue`
                            ];
                        }
                    }
                }
            }
        }
    });
    } catch (err) {

    console.error(err);

    } finally {
            loadingEl.style.display = 'none';
    }

}