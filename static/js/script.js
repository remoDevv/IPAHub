document.addEventListener('DOMContentLoaded', function() {
    // Dropdown menu functionality
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('.dropdown-trigger');
        const content = dropdown.querySelector('.dropdown-content');
        
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            content.style.display = content.style.display === 'block' ? 'none' : 'block';
        });
        
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                content.style.display = 'none';
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });

    // File upload preview
    const fileInput = document.querySelector('input[type="file"]');
    const preview = document.querySelector('#file-preview');
    
    if (fileInput && preview) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Advanced search functionality
    const searchForm = document.querySelector('#search-form');
    const searchResults = document.querySelector('#search-results');
    
    if (searchForm && searchResults) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = searchForm.querySelector('input[name="query"]').value;
            
            // Normally, we'd use fetch here, but as per the guidelines, we'll avoid it
            // Instead, we'll submit the form and let the server handle the search
            searchForm.submit();
        });
    }
});
