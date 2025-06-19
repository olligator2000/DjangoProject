document.addEventListener("DOMContentLoaded", () => {
    const ratingStars = document.querySelectorAll(".rating-star");
    const ratingValue = document.getElementById("custom-rating-value");

    ratingStars.forEach(star => {
        star.addEventListener("click", async () => {
            const rating = star.dataset.rating;

            try {
                const response = await fetch('/products/rate_product/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: `product_id=${star.closest('.custom-product-card').querySelector('.custom-add-to-cart').dataset.productId}&rating=${rating}`
                });

                const data = await response.json();

                if (data.status === 'success') {
                    // Обновляем отображение рейтинга
                    ratingValue.textContent = data.average_rating;
                    document.querySelector('.custom-rating-star-icon').style.display = 'inline-block';
                    // Обновляем звезды
                    ratingStars.forEach((s, i) => {
                        if (i < rating) {
                            s.classList.add('filled');
                        } else {
                            s.classList.remove('filled');
                        }
                    });
                } else {
                    alert(data.message || 'Ошибка при сохранении оценки');
                }
            } catch (error) {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при отправке оценки');
            }
        });
    });
});