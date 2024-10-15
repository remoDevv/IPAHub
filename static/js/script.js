document.addEventListener('DOMContentLoaded', function() {
    // Star rating functionality
    const ratingInput = document.querySelector('#rating');
    const ratingStars = document.querySelector('.rating-stars');

    if (ratingInput && ratingStars) {
        const stars = ratingStars.querySelectorAll('.star');

        stars.forEach(star => {
            star.addEventListener('click', function() {
                ratingInput.value = this.dataset.value;
                updateStars();
            });

            star.addEventListener('mouseover', function() {
                const hoverValue = this.dataset.value;
                highlightStars(hoverValue);
            });

            star.addEventListener('mouseout', function() {
                const selectedValue = ratingInput.value;
                highlightStars(selectedValue);
            });
        });

        function updateStars() {
            const selectedValue = ratingInput.value;
            highlightStars(selectedValue);
        }

        function highlightStars(value) {
            stars.forEach(star => {
                star.innerHTML = star.dataset.value <= value ? '&#9733;' : '&#9734;';
                star.classList.toggle('filled', star.dataset.value <= value);
            });
        }

        // Initialize stars based on the initial value
        updateStars();
    }

    // Prevent double submission of review form
    const reviewForm = document.querySelector('.review-form form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('input[type="submit"]');
            if (submitButton && submitButton.getAttribute('data-submitted')) {
                e.preventDefault();
            } else {
                if (submitButton) {
                    submitButton.setAttribute('data-submitted', 'true');
                    submitButton.value = 'Submitting...';
                    submitButton.disabled = true;
                }
            }
        });
    }
});
