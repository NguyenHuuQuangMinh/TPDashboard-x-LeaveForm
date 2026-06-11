function showFileName(input) {
  const label = document.getElementById('drop-label');
  if (input.files && input.files[0]) {
    label.innerHTML = '📄 <strong>' + input.files[0].name + '</strong>';
  }
}
function handleDrop(e) {
  e.preventDefault();
  document.getElementById('drop-zone').style.borderColor = '#d0d0d0';
  const file = e.dataTransfer.files[0];
  if (file) {
    const input = document.getElementById('import-file-input');
    const dt = new DataTransfer();
    dt.items.add(file);
    input.files = dt.files;
    showFileName(input);
  }
}