document.addEventListener('DOMContentLoaded', function() {
    // 1. Обработка оценки товара (звёздочки)
    const ratingStars = document.querySelectorAll('.rating-star');
    let selectedRating = 0;

    if (ratingStars.length > 0) {
        ratingStars.forEach(star => {
            star.addEventListener('click', function() {
                selectedRating = parseInt(this.getAttribute('data-rating'));
                console.log('Выбрана оценка:', selectedRating);

                // Обновляем визуальное отображение звёзд
                ratingStars.forEach((s, index) => {
                    if (index < selectedRating) {
                        s.classList.add('filled');
                    } else {
                        s.classList.remove('filled');
                    }
                });

                // Обновляем скрытое поле с рейтингом
                const ratingInput = document.getElementById('rating-input');
                if (ratingInput) {
                    ratingInput.value = selectedRating;
                }

                // Отправляем рейтинг на сервер
                sendRating(selectedRating);
            });
        });
    }

    // 2. Обработка отправки отзыва
    const reviewForm = document.querySelector('.review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Отправка отзыва...');

            const textarea = this.querySelector('textarea[name="text"]');
            const text = textarea.value.trim();

            // Валидация: проверка на пустой отзыв
            if (!text) {
                showNotification('Пожалуйста, напишите отзыв перед отправкой', 'warning');
                textarea.focus();
                textarea.classList.add('error');
                setTimeout(() => textarea.classList.remove('error'), 2000);
                return;
            }

            const formData = new FormData(this);
            const productId = window.location.pathname.split('/')[2];

            fetch(`/products/${productId}/review/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                }
            })
            .then(response => {
                if (!response.ok) throw new Error('Ошибка сети');
                return response.json();
            })
            .then(data => {
                console.log('Ответ сервера:', data);
                if (data.status === 'success') {
                    showNotification('Отзыв успешно добавлен!', 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    throw new Error(data.message || 'Ошибка при отправке отзыва');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification(error.message || 'Произошла ошибка при отправке отзыва', 'error');
            });
        });
    }

    // 3. Обработка кнопки "В избранное"
    const favoriteBtns = document.querySelectorAll('.custom-favorite-btn');
    favoriteBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');

            fetch(this.href, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: `csrfmiddlewaretoken=${getCookie('csrftoken')}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'added' || data.status === 'removed') {
                    // Обновляем только правую колонку
                    fetch(window.location.href, {
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        }
                    })
                    .then(response => response.text())
                    .then(html => {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const newRightColumn = doc.querySelector('.custom-right-column');
                        document.getElementById('product-favorite-section').innerHTML = newRightColumn.innerHTML;
                        // Повторно инициализируем обработчики событий для новой кнопки
                        initFavoriteButtons();
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Произошла ошибка', 'error');
            });
        });
    });

    // 4. Инициализация текущего рейтинга пользователя (если есть)
    const initialRating = document.getElementById('rating-input')?.value;
    if (initialRating && initialRating > 0) {
        const stars = document.querySelectorAll('.rating-star');
        stars.forEach((star, index) => {
            if (index < initialRating) {
                star.classList.add('filled');
            }
        });
    }

    // Функция отправки рейтинга на сервер
    function sendRating(rating) {
        const productId = window.location.pathname.split('/')[2];
        const formData = new FormData();
        formData.append('rating', rating);
        formData.append('csrfmiddlewaretoken', document.querySelector('input[name="csrfmiddlewaretoken"]').value);

        fetch(`/products/${productId}/rate/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Ошибка сети');
            return response.json();
        })
        .then(data => {
            console.log('Ответ сервера:', data);
            if (data.status === 'success') {
                // Обновляем отображение среднего рейтинга
                const ratingValueElement = document.getElementById('custom-rating-value');
                if (ratingValueElement) {
                    ratingValueElement.textContent = data.average_rating;
                }
                showNotification('Ваша оценка сохранена!', 'success');
            } else {
                throw new Error(data.message || 'Неизвестная ошибка');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showNotification(error.message || 'Ошибка при сохранении оценки', 'error');
        });
    }

    // Функция для показа уведомлений
    function showNotification(message, type = 'success') {
        // Удаляем предыдущие уведомления
        const existingNotice = document.querySelector('.custom-notification');
        if (existingNotice) existingNotice.remove();

        const notification = document.createElement('div');
        notification.className = `custom-notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Анимация появления
        setTimeout(() => notification.classList.add('show'), 10);

        // Автоматическое скрытие через 3 секунды
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Функция для получения CSRF-токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Функция для повторной инициализации кнопок избранного после обновления DOM
    function initFavoriteButtons() {
        document.querySelectorAll('.custom-favorite-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const productId = this.getAttribute('data-product-id');

                fetch(this.href, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: `csrfmiddlewaretoken=${getCookie('csrftoken')}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'added' || data.status === 'removed') {
                        fetch(window.location.href, {
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                            }
                        })
                        .then(response => response.text())
                        .then(html => {
                            const parser = new DOMParser();
                            const doc = parser.parseFromString(html, 'text/html');
                            const newRightColumn = doc.querySelector('.custom-right-column');
                            document.getElementById('product-favorite-section').innerHTML = newRightColumn.innerHTML;
                            initFavoriteButtons();
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Произошла ошибка', 'error');
                });
            });
        });
    }
});