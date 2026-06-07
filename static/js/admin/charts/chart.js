import { loadQuarterChart } from './revenue-quarter.js';
import { loadAgentChart } from './revenue-agent.js';
import { loadTrendChart } from './revenue-trend.js';
import { openRevenueDetail } from './detail-modal.js';

document.addEventListener('DOMContentLoaded', () => {

    loadQuarterChart();
    loadAgentChart();
    loadTrendChart();

    const yearQuarterFilter =
        document.getElementById('chartYearFilter');
    const yearAgentFilter =
        document.getElementById('agentYearFilter');
    const yearTrendFilter =
        document.getElementById('trendYearFilter');

    if (yearQuarterFilter) {

        yearQuarterFilter.addEventListener('change', () => {
            loadQuarterChart();
        });
    }
    if (yearAgentFilter) {

        yearAgentFilter.addEventListener('change', () => {
            loadAgentChart();
        });
    }
    if (yearTrendFilter) {

        yearTrendFilter.addEventListener('change', () => {
            loadTrendChart();
        });
    }
});