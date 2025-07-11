document.addEventListener('DOMContentLoaded', function() {
    // Инициализация кнопок избранного
    initFavoriteButtons();

    // Функция для инициализации кнопок избранного
    function initFavoriteButtons() {
        document.querySelectorAll('.favorite-btn').forEach(btn => {
            // Удаляем старые обработчики, чтобы избежать дублирования
            btn.removeEventListener('click', handleFavoriteClick);
            btn.addEventListener('click', handleFavoriteClick);
        });
    }

    // Обработчик клика по кнопке избранного
    function handleFavoriteClick(e) {
        e.preventDefault();
        const btn = this;
        const productId = btn.getAttribute('data-product-id');
        const url = btn.getAttribute('href');

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: `csrfmiddlewaretoken=${getCookie('csrftoken')}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'added' || data.status === 'removed') {
                // Обновляем только кнопку
                btn.classList.toggle('active');
                btn.setAttribute('title',
                    btn.classList.contains('active')
                        ? 'Удалить из избранного'
                        : 'В избранное');

                showNotification(
                    data.status === 'added'
                        ? 'Товар добавлен в избранное'
                        : 'Товар удален из избранное',
                    'success');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Произошла ошибка', 'error');
        });
    }

    // Функция для показа уведомлений
    function showNotification(message, type = 'success') {
        const existingNotice = document.querySelector('.custom-notification');
        if (existingNotice) existingNotice.remove();

        const notification = document.createElement('div');
        notification.className = `custom-notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add('show'), 10);

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

    // Экспортируем функцию для повторной инициализации
    window.reinitFavorites = initFavoriteButtons;
});