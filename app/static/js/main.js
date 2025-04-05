'use strict';

document.addEventListener('DOMContentLoaded', function() {

    const uploadForm = document.getElementById('uploadForm');
    const spinnerContainer = document.getElementById('spinnerContainer');
    const fileInput = document.getElementById('fileInput');
    const resultsSection = document.getElementById('resultsSection');
    const flashContainer = document.getElementById('flash-message-container'); // Container for flash messages

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            if (!fileInput || !fileInput.value || !uploadForm.checkValidity()) {
                console.log("Form not valid or no file selected, preventing JS spinner/cleanup.");
                uploadForm.classList.add('was-validated');
                event.preventDefault();
                event.stopPropagation();
                return;
            }

            if (flashContainer) {
                flashContainer.innerHTML = '';
            }
            if (resultsSection) {
                resultsSection.style.display = 'none';
            }
            const submitButton = uploadForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Uploading & Scanning...
                `;
            }
            if (spinnerContainer) {
                 spinnerContainer.style.display = 'block';
            }

        });
    } else {
        console.error("Element with ID 'uploadForm' not found.");
    }
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    // Prevent submission *again* just in case
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });

}); // End of DOMContentLoaded listener