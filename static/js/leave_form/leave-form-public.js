function showToast(
    message,
    category = 'success'
) {

    const overlay =
        document.createElement('div');

    overlay.className =
        'toast-overlay';

    overlay.innerHTML = `
        <div class="toast ${category}">
            ${message}
        </div>
    `;

    document.body.appendChild(
        overlay
    );

    setTimeout(() => {

        overlay.remove();

    }, 2200);

}

function goToLeave() {
  var id = (document.getElementById('emp-id-input').value || '').trim();
  if (!id) { alert('Please enter an Employee ID.'); return; }
  window.location.href = '/leave/' + id;
}
document.getElementById('emp-id-input').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') goToLeave();
});