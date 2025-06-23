document.addEventListener('DOMContentLoaded', function () {
    // Переключение вкладок профиля
    document.querySelectorAll('.profile-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            // Удаляем активный класс у всех табов и контента
            document.querySelectorAll('.profile-tab, .tab-content').forEach(el => {
                el.classList.remove('active');
            });

            // Добавляем активный класс текущему табу и соответствующему контенту
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });

    // Загрузка фото профиля
    const photoUpload = document.getElementById('photoUpload');
    if (photoUpload) {
        photoUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('fileName').textContent = file.name;

                // Превью загруженного изображения
                const reader = new FileReader();
                reader.onload = function(event) {
                    document.getElementById('profilePhoto').src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Обработка удаления из избранного
    document.querySelectorAll('.remove-favorite-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const url = `/users/favorites/remove/${productId}/`;
            const productItem = this.closest('.favorite-item');

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `csrfmiddlewaretoken=${getCookie('csrftoken')}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Плавное удаление элемента
                    productItem.style.transition = 'opacity 0.3s';
                    productItem.style.opacity = '0';

                    setTimeout(() => {
                        productItem.remove();

                        // Проверяем, есть ли еще избранные товары
                        if (document.querySelectorAll('.favorite-item').length === 0) {
                            // Показываем сообщение "нет избранных товаров"
                            document.querySelector('.favorites-list').innerHTML = `
                                <div class="no-favorites" style="text-align: center; padding: 30px; color: #666;">
                                    <i class="far fa-heart" style="font-size: 24px; color: #e74c3c;"></i>
                                    <div style="margin-top: 10px;">У вас пока нет избранных товаров</div>
                                </div>
                            `;
                        }
                    }, 300);
                } else {
                    alert('Ошибка при удалении из избранного');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка');
            });
        });
    });

    // Обработка кликов по сердечкам для рейтинга товаров
    const hearts = document.querySelectorAll('.heart');
    hearts.forEach(heart => {
        heart.addEventListener('click', function () {
            const ratingContainer = this.parentElement;
            const productId = ratingContainer.dataset.productId;
            const rating = this.dataset.rating;

            fetch('/products/rate_product/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: `product_id=${productId}&rating=${rating}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Обновляем отображение сердечек
                    const hearts = ratingContainer.querySelectorAll('.heart');
                    hearts.forEach(h => {
                        h.classList.toggle('filled', h.dataset.rating <= rating);
                    });
                    alert(data.message);
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при сохранении оценки.');
            });
        });
    });

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

    function toggleFavorite(event, productId) {
        event.preventDefault();

        fetch(`/users/favorites/add/${productId}/`, {
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
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
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

    // Обработка удаления отзывов
    document.querySelectorAll('.remove-review-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.href;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: `csrfmiddlewaretoken=${getCookie('csrftoken')}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const reviewItem = this.closest('.review-item');
                    reviewItem.style.transition = 'opacity 0.3s';
                    reviewItem.style.opacity = '0';

                    setTimeout(() => {
                        reviewItem.remove();

                        // Проверяем, есть ли еще отзывы
                        if (document.querySelectorAll('.review-item').length === 0) {
                            document.querySelector('.reviews-list').innerHTML = `
                                <div class="no-reviews">
                                    <i class="far fa-comment-alt"></i>
                                    <div>Вы ещё не оставляли отзывов</div>
                                </div>
                            `;
                        }
                    }, 300);
                } else {
                    alert('Ошибка при удалении отзыва');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка');
            });
        });
    });
});