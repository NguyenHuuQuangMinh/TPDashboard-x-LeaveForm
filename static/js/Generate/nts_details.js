const rows = document.querySelectorAll('.msg-row');
const overlay = document.getElementById('detailOverlay');
const panel = document.getElementById('detailPanel');
const panelClose = document.getElementById('panelClose');
const panelLoading = document.getElementById('panelLoading');
const panelBody = document.getElementById('panelBody');

rows.forEach(row => {
  row.addEventListener('click', () => {
    const code = row.dataset.code;
    const message = row.querySelector('.td-msg').dataset.message;
    openPanel(code, row.querySelector('.td-name').textContent.trim(), message);
  });
});

panelClose.addEventListener('click', closePanel);
overlay.addEventListener('click', e => { if (e.target === overlay) closePanel(); });

function openPanel(code, name, message) {
  overlay.classList.add('active');
  panelLoading.style.display = 'flex';
  panelBody.style.display = 'none';
  document.getElementById('panelAgentName').textContent = name + ' (' + code + ')';
  document.getElementById('panelMessageText').innerHTML =
    message || '-';
  fetch(`/partial/nts/agent/${code}`)
    .then(r => r.json())
    .then(data => {
      renderRevenue(data.yearly);
      renderContacts(data.contacts);
      panelLoading.style.display = 'none';
      panelBody.style.display = 'block';
    });
}

function closePanel() {
  overlay.classList.remove('active');
}

function renderRevenue(yearly) {
  // Group by year
  const years = {};
  yearly.forEach(r => {
    if (!years[r.year]) years[r.year] = {};
    years[r.year][r.month] = r.profit;
  });

  const months = [1,2,3,4,5,6,7,8,9,10,11,12];
  let html = '';
  for (const year of Object.keys(years).sort()) {
    const row = years[year];
    let yearTotal = 0;
    let monthCells = months.map(m => {
      const val = row[m] || 0;
      yearTotal += val;
      return `<td>${val ? val.toLocaleString('en-US', {minimumFractionDigits:3, maximumFractionDigits:3}) : '0'}</td>`;
    }).join('');

    // Quarters
    const q = [0,0,0,0];
    months.forEach(m => { q[Math.floor((m-1)/3)] += row[m] || 0; });

    html += `
      <div class="rev-year-title">${year} Revenue</div>
      <div class="rev-scroll">
        <table class="rev-table">
          <thead><tr>
            ${months.map(m => `<th>${String(m).padStart(2,'0')}/${year}</th>`).join('')}
            <th>Year Total</th>
          </tr></thead>
          <tbody><tr>${monthCells}<td>${yearTotal.toLocaleString('en-US', {minimumFractionDigits:1})}</td></tr></tbody>
        </table>
      </div>
      <div class="rev-quarters">
        <table class="rev-table">
          <thead><tr><th>NAME</th><th>Quarter 1</th><th>Quarter 2</th><th>Quarter 3</th><th>Quarter 4</th></tr></thead>
          <tbody><tr>
            <td id="panelAgentNameQ"></td>
            ${q.map(v => `<td>${v ? v.toLocaleString('en-US', {minimumFractionDigits:3}) : '0'}</td>`).join('')}
          </tr></tbody>
        </table>
      </div>`;
  }
  document.getElementById('revenueYears').innerHTML = html || '<p style="color:#888;padding:12px 0">No revenue data</p>';
  // fill agent name in quarter rows
  document.querySelectorAll('#panelAgentNameQ').forEach(el => {
    el.textContent = document.getElementById('panelAgentName').textContent.split('(')[0].trim();
  });
}

function renderContacts(contacts) {
  const tbody = document.getElementById('contactBody');
  if (!contacts.length) {
    tbody.innerHTML = '<tr><td colspan="5" style="color:#888;text-align:center">No contact info</td></tr>';
    return;
  }
  tbody.innerHTML = contacts.map((c, i) => `
    <tr>
      <td>${i+1}</td>
      <td>${c.contact_name || '-'}</td>
      <td>${c.title || '-'}</td>
      <td>${c.email || '-'}</td>
      <td>${c.phone || '-'}</td>
    </tr>`).join('');
}