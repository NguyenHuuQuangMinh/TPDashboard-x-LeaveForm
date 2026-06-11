function goToLeave() {
  const uid = (document.getElementById('emp-id-input').value || '').trim();
  const security = document.getElementById("security-input").value.trim();
  if (!uid || !security) {
        showToast(
            'Please enter both Employee ID and Security Code.',
            'error'
        );
        return;
  }
  window.location.href = `/leave/${uid}/${security}`;
}
['emp-id-input', 'security-input'].forEach(id => {
    document.getElementById(id).addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            goToLeave();
        }
    });
});

