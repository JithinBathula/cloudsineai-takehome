'use strict';

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('uploadForm');
  const fileInput = document.getElementById('fileInput');
  const spinner = document.getElementById('spinnerContainer');
  const flashContainer = document.getElementById('flash-message-container');
  const resultsSection = document.getElementById('resultsSection');

  if (!form) return console.error("Form not found");

  form.addEventListener('submit', function (e) {
    if (!form.checkValidity() || !fileInput?.files?.length) {
      e.preventDefault();
      e.stopPropagation();
      form.classList.add('was-validated');
      return;
    }

    // Clear old UI
    flashContainer.innerHTML = '';
    if (resultsSection) resultsSection.style.display = 'none';

    const btn = form.querySelector('button[type="submit"]');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading & Scanning...`;
    }

    if (spinner) spinner.style.display = 'block';
  });

  // Bootstrap validation
  Array.from(document.querySelectorAll('.needs-validation')).forEach(f => {
    f.addEventListener('submit', e => {
      if (!f.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      f.classList.add('was-validated');
    });
  });
});
