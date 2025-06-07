document.addEventListener('DOMContentLoaded', initCart);

function initCart() {
    const isAuthenticated = window.isAuthenticated;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    if (!isAuthenticated) {
        document.querySelectorAll('.add-to-cart-btn, .quantity-btn, .clear-cart-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                alert('Для управления корзиной войдите в систему');
                window.location.href = window.loginUrl;
            });
        });
        return;
    }

    if (!csrfToken) {
        console.error('CSRF token not found');
        alert('Ошибка: CSRF-токен не найден. Перезагрузите страницу.');
        return;
    }

    setupHandlers();
}

function setupHandlers() {
    // Обработчик для добавления в корзину
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', () => addToCart(btn.dataset.productId));
    });

    // Делегирование событий для кнопок "+" и "−" и очистки корзины
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('quantity-btn')) {
            e.preventDefault();
            const { basketId, action } = e.target.dataset;
            if (!basketId || !action) {
                console.error('Missing basket ID or action');
                return;
            }
            updateCart(basketId, action);
        } else if (e.target.classList.contains('clear-cart-btn')) {
            e.preventDefault();
            if (confirm('Очистить всю корзину?')) clearCart();
        }
    });
}

async function addToCart(productId) {
    try {
        // Находим ближайший элемент ввода количества или используем значение по умолчанию 1
        let quantity = 1;
        const quantityInput = document.querySelector(`.add-to-cart-btn[data-product-id="${productId}"]`)
                            .closest('.product-card')?.querySelector('.quantity-input');

        if (quantityInput) {
            quantity = parseInt(quantityInput.value) || 1;
        }

        const response = await fetch(`/products/add_to_cart_ajax/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ quantity: quantity })
        });

        if (!response.ok) {
            const data = await response.json();
            if (data.message === 'Товар отсутствует на складе') {
                alert('Товар отсутствует на складе');
            } else {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return;
        }

        const data = await response.json();

        if (data.status === 'success') {
            // Обновляем корзину
            const cartContainer = document.getElementById('cart-container');
            if (cartContainer) {
                cartContainer.innerHTML = data.cart_html;
            }

            // Обновляем бейдж с количеством товаров
            updateCartBadge(data.total_items);

            // Обновляем общую сумму в шапке
            const headerTotalElement = document.getElementById('header-cart-total');
            if (headerTotalElement) {
                headerTotalElement.textContent = `${data.total_sum} ₽`;
            }

            // Показываем уведомление о добавлении
            showToast('Товар добавлен в корзину');
        } else {
            alert(data.message || 'Ошибка при добавлении товара в корзину');
        }
    } catch (error) {
        console.error('Add to cart failed:', error);
        alert(error.message !== 'HTTP error! Status: 400' ? `Ошибка: ${error.message}` : 'Товар отсутствует на складе');
    }
}

// Вспомогательная функция для показа уведомлений
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

async function updateCart(basketId, action) {
    const cartItem = document.querySelector(`.cart-item[data-basket-id="${basketId}"]`);
    if (!cartItem) {
        console.error('Cart item not found');
        return;
    }

    const quantityElement = cartItem.querySelector('.quantity-value');
    const sumElement = cartItem.querySelector('.item-details');
    const totalElement = document.querySelector('.total-price');
    const headerTotalElement = document.getElementById('header-cart-total'); // Изменено на header-cart-total

    const originalQuantity = quantityElement.textContent;
    const originalSum = sumElement.textContent;

    try {
        const response = await fetch(`/products/update_basket_ajax/${basketId}/${action}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken(), 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            const data = await response.json();
            if (response.status === 400 && data.message && data.message.startsWith('Недостаточно товара на складе. Доступно: ')) {
                const availableQuantity = data.message.split(' ').pop();
                alert(`На складе всего ${availableQuantity} штук`);
            } else {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            quantityElement.textContent = originalQuantity;
            sumElement.textContent = originalSum;
            return;
        }

        const data = await response.json();

        if (data.status === 'success') {
            quantityElement.textContent = data.quantity;
            sumElement.textContent = `${data.sum} ₽`;
            if (totalElement) totalElement.textContent = `${data.total_sum} ₽`;
            if (headerTotalElement) headerTotalElement.textContent = `${data.total_sum} ₽`; // Синхронизация с total-price
        } else if (data.status === 'removed') {
            cartItem.style.transition = 'opacity 0.3s';
            cartItem.style.opacity = '0';
            setTimeout(() => cartItem.remove(), 300);
            if (totalElement) totalElement.textContent = `${data.total_sum} ₽`;
            if (headerTotalElement) headerTotalElement.textContent = `${data.total_sum} ₽`; // Синхронизация с total-price
            if (data.total_sum === 0) {
                document.querySelector('.cart-items-container').innerHTML = '<div class="basket-pusto">В корзине нет товаров</div>';
                if (headerTotalElement) headerTotalElement.textContent = 'Корзина пуста';
            }
        } else {
            quantityElement.textContent = originalQuantity;
            sumElement.textContent = originalSum;
            alert(data.message || 'Ошибка при обновлении корзины');
        }
    } catch (error) {
        console.error('Update cart failed:', error);
        quantityElement.textContent = originalQuantity;
        sumElement.textContent = originalSum;
        alert(`Ошибка: ${error.message}`);
    }
}

async function clearCart() {
    try {
        const response = await fetch('/products/clear_basket_ajax/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken(), 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();

        if (data.status === 'success' || data.status === 'empty') {
            document.getElementById('cart-container').innerHTML = data.cart_html || renderEmptyCart();
            updateCartBadge(0);
            const headerTotalElement = document.getElementById('header-cart-total');
            if (headerTotalElement) headerTotalElement.textContent = 'Корзина пуста'; // Синхронизация
        } else {
            alert(data.message || 'Ошибка при очистке корзины');
        }
    } catch (error) {
        console.error('Clear cart failed:', error);
        alert(`Ошибка: ${error.message}`);
    }
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}

function updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'block' : 'none';
    }
}

function renderEmptyCart() {
    return `
        <div class="cart-sidebar">
            <div class="cart-header">
                <h2 class="cart-title">Корзина</h2>
            </div>
            <div class="basket-pusto">В корзине нет товаров</div>
        </div>
    `;
}

// Обработчики для кнопок "+" и "-"
document.querySelectorAll('.quantity-increase').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        const input = btn.parentElement.querySelector('.quantity-input');
        const max = parseInt(input.getAttribute('max')) || Infinity;
        if (parseInt(input.value) < max) {
            input.value = parseInt(input.value) + 1;
        }
    });
});

document.querySelectorAll('.quantity-decrease').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        const input = btn.parentElement.querySelector('.quantity-input');
        if (parseInt(input.value) > 1) {
            input.value = parseInt(input.value) - 1;
        }
    });
});

// Валидация ввода
document.querySelectorAll('.quantity-input').forEach(input => {
    input.addEventListener('change', (e) => {
        const value = parseInt(e.target.value);
        const min = parseInt(e.target.getAttribute('min')) || 1;
        const max = parseInt(e.target.getAttribute('max')) || Infinity;

        if (isNaN(value) || value < min) {
            e.target.value = min;
        } else if (value > max) {
            e.target.value = max;
        } else {
            e.target.value = value;
        }
    });
});