function goToLeave() {
  var id = (document.getElementById('emp-id-input').value || '').trim();
  if (!id) { alert('Please enter an Employee ID.'); return; }
  window.location.href = '/leave/' + id;
}
document.getElementById('emp-id-input').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') goToLeave();
});