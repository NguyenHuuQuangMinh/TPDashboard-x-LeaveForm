var totalRows = window.APP_DATA.totalRows;
var REJECT_BASE = window.APP_DATA.rejectBase;

/* ── Tabs ── */
function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(function(b) { b.classList.remove('active'); });
  document.querySelectorAll('.tab-panel').forEach(function(p) { p.classList.remove('active'); });
  document.getElementById('tab-btn-' + tab).classList.add('active');
  document.getElementById('panel-' + tab).classList.add('active');
  document.getElementById('search-area').style.display = tab === 'overview' ? 'flex' : 'none';
}

/* ── Search ── */
function doFilter() {
  if (totalRows === 0) return;
  var q  = document.getElementById('usearch').value.trim();
  document.getElementById('clrbtn').style.display = q ? 'inline' : 'none';
  var ql = q.toLowerCase();
  var rows = document.querySelectorAll('#tbody tr');
  var visible = 0;
  rows.forEach(function(row) {
    var uid = (row.getAttribute('data-uid') || '').toLowerCase();
    var name     = row.getAttribute('data-name') || '';
    var username = row.getAttribute('data-username') || '';
    var match = !q || uid === q || username.indexOf(ql) !== -1 || name.indexOf(ql) !== -1;
    row.style.display = match ? '' : 'none';
    if (match) visible++;
  });
  document.getElementById('nores').style.display = (visible === 0 && q) ? '' : 'none';
  document.getElementById('qspan').textContent = q;
  document.getElementById('cnt').textContent = q ? visible + ' / ' + totalRows + ' nhân viên' : '';
}

function doClear() {
  document.getElementById('usearch').value = '';
  document.getElementById('clrbtn').style.display = 'none';
  doFilter();
  document.getElementById('usearch').focus();
}

/* ── Reject modal ── */
function openReject(entryId, name) {
  document.getElementById('reject-name').textContent = name;
  document.getElementById('reject-form').action = REJECT_BASE + entryId;
  document.getElementById('reject-modal').classList.add('open');
}
function closeReject() {
  document.getElementById('reject-modal').classList.remove('open');
  document.querySelector('#reject-form textarea').value = '';
}
document.getElementById('reject-modal').addEventListener('click', function(e) {
  if (e.target === this) closeReject();
});

/* ── Init tab from URL ── */
(function() {
  var params = new URLSearchParams(window.location.search);
  switchTab(params.get('tab') === 'pending' ? 'pending' : 'overview');
})();

