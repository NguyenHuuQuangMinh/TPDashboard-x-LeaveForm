import { openRevenueDetail }
from './detail-modal.js';

let trendChart = null;
let revenueMonthlyDetailCache = [];
export async function loadTrendChart() {

    const year =
        document.getElementById('trendYearFilter')?.value;

    const params =
        new URLSearchParams(window.location.search);

    if (year) {
        params.set('year', year);
    } else {
        params.delete('year');
    }

    const response =
        await fetch(
            `/admin/chart/revenue-monthly?${params.toString()}`
        );

    const data = await response.json();

    const ctx =
        document.getElementById('monthlyTrendChart');

    if (!ctx) return;

    if (trendChart) {
        trendChart.destroy();
    }

    trendChart = new Chart(ctx, {

        type: 'line',

        data: {

            labels:
                data.map(r => r.month),

            datasets: [{

                label: 'Revenue',

                data:
                    data.map(r => Number(r.revenue)),

                borderColor: '#B08D4A',

                backgroundColor:
                    'rgba(176,141,74,.15)',

                tension: 0.35,

                fill: true,

                pointRadius: 4,

                pointHoverRadius: 8,

                pointBackgroundColor: '#B08D4A',

                pointBorderColor: '#fff',

                pointBorderWidth: 2,

                borderWidth: 3
            }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            animation: {

                duration: 1200,

                easing: 'easeOutQuart'
            },

            interaction: {

                mode: 'index',

                intersect: false
            },

            plugins: {

                legend: {
                    display: false
                },

                tooltip: {

                    backgroundColor: '#1e1e2d',

                    titleColor: '#fff',

                    bodyColor: '#ddd',

                    padding: 12,

                    cornerRadius: 10,

                    displayColors: false,

                    callbacks: {

                        title: function(context) {

                            return `Month: ${context[0].label}`;
                        },

                        label: function(context) {

                            const current =
                                context.raw;

                            const dataset =
                                context.dataset.data;

                            const index =
                                context.dataIndex;

                            let growthText =
                                'First month';

                            if (index > 0) {

                                const prev =
                                    dataset[index - 1];

                                if (prev > 0) {

                                    const growth =
                                        (
                                            (
                                                (current - prev)
                                                / prev
                                            ) * 100
                                        ).toFixed(1);

                                    const icon =
                                        growth >= 0
                                        ? '▲'
                                        : '▼';

                                    growthText =
                                        `${icon} ${growth}% vs previous month`;
                                }
                            }

                            return [
                                `Revenue: ${current.toLocaleString('en-US')} USD`,
                                growthText
                            ];
                        }
                    }
                }
            },

            scales: {

                x: {

                    grid: {
                        display: false
                    },

                    ticks: {
                        color: '#9CA3AF'
                    }
                },

                y: {

                    grid: {
                        color: 'rgba(255,255,255,0.05)'
                    },

                    ticks: {

                        color: '#9CA3AF',

                        callback: value =>
                            value.toLocaleString('en-US')
                    }
                }
            },

            onClick: async (evt, elements) => {

                if (!elements.length) return;

                const index =
                    elements[0].index;

                const month =
                    data[index].month;

                const cacheKey =
                    `${month}_${year || 'all'}_${params.toString()}`;

                let detailData =
                    revenueMonthlyDetailCache[cacheKey];

                // ===== FETCH FIRST TIME =====

                if (!detailData) {

                    const detailParams =
                        new URLSearchParams({

                            month,

                            ...Object.fromEntries(
                                params.entries()
                            )
                        });

                    const response =
                        await fetch(
                            `/admin/chart/revenue-monthly-detail?${detailParams.toString()}`
                        );

                    detailData =
                        await response.json();

                    revenueMonthlyDetailCache[cacheKey] =
                        detailData;
                }

                await openRevenueDetail({

                    title: `Revenue Detail - Month ${month}`,

                    month,
                    year,

                    data: detailData,

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
            }
        }
    });
}