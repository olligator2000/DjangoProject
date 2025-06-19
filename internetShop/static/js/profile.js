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
});