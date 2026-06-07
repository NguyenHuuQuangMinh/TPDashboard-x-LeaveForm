import { openRevenueDetail }
from './detail-modal.js';

let agentChart = null;
let topAgentDetailCache = []
export async function loadAgentChart() {

    const year =
        document.getElementById('agentYearFilter')?.value;

    const params =
        new URLSearchParams(window.location.search);

    if (year) {
        params.set('year', year);
    }

    const response =
        await fetch(
            `/admin/chart/top-agents?${params.toString()}`
        );

    const data = await response.json();

    const ctx =
        document.getElementById('topAgentsChart');

    if (!ctx) return;

    if (agentChart) {
        agentChart.destroy();
    }

    agentChart = new Chart(ctx, {

        type: 'bar',

        data: {
            labels:
                data.map(r => r.name || r.agent_code),

            datasets: [{
                label: 'Revenue',

                data:
                    data.map(r => Number(r.revenue)),

                backgroundColor: '#B08D4A',
                borderRadius: 8
            }]
        },

        options: {

            indexAxis: 'y',

            responsive: true,
            maintainAspectRatio: false,

            plugins: {

                legend: {
                    display: false
                },

                tooltip: {
                    callbacks: {

                        title: function(context) {

                            const row =
                                data[context[0].dataIndex];

                            return row.name
                                ? `${row.name} (${row.agent_code})`
                                : row.agent_code;
                        },

                        label: function(context) {

                            const value =
                                context.raw;

                            const total =
                                context.dataset.data.reduce(
                                    (a, b) => a + b,
                                    0
                                );

                            const percent =
                                (
                                    (value / total) * 100
                                ).toFixed(1);

                            return [
                                `Revenue: ${value.toLocaleString('en-US')} USD`,
                                `${percent}% of Top 10`
                            ];
                        }
                    }
                }
            },

            scales: {

            x: {

                ticks: {

                    color: '#9CA3AF',

                    callback: value =>
                        value.toLocaleString('en-US')
                },

                grid: {
                    color: 'rgba(255,255,255,0.05)'
                }
            },

            y: {

                ticks: {

                    autoSkip: false,

                    font: {
                        size: 11
                    }
                },

                grid: {
                    display: false
                }
            }
        },

            onClick: async (evt, elements) => {

                if (!elements.length) return;

                const index =
                    elements[0].index;

                const row =
                    data[index];

                const agentCode =
                    row.agent_code;

                const cacheKey =
                    `${agentCode}_${year || 'all'}_${params.toString()}`;

                let detailData =
                    topAgentDetailCache[cacheKey];

                // ===== FETCH FIRST TIME =====

                if (!detailData) {

                    const detailParams =
                        new URLSearchParams({

                            agent_code: agentCode,

                            ...Object.fromEntries(
                                params.entries()
                            )
                        });

                    const response =
                        await fetch(
                            `/admin/chart/top-agents-detail?${detailParams.toString()}`
                        );

                    detailData =
                        await response.json();

                    topAgentDetailCache[cacheKey] =
                        detailData;
                }

                await openRevenueDetail({

                    title:
                        `Revenue Detail - ${row.name || agentCode}`,

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