document.addEventListener('DOMContentLoaded', initCart);

function initCart() {
    const isAuthenticated = window.isAuthenticated;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    if (!isAuthenticated) {
        document.querySelectorAll('.add-to-cart-btn, .quantity-btn, .clear-cart-btn').forEach(btn => {
            btn.removeEventListener('click', handleAuthRedirect);
            btn.addEventListener('click', handleAuthRedirect);
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

function handleAuthRedirect() {
    alert('Для управления корзиной войдите в систему');
    window.location.href = window.loginUrl;
}

function setupHandlers() {
    // Удаляем все старые обработчики перед добавлением новых
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.removeEventListener('click', handleAddToCart);
        btn.addEventListener('click', handleAddToCart);
    });

    document.removeEventListener('click', handleCartActions);
    document.addEventListener('click', handleCartActions);

    function handleAddToCart(e) {
        e.preventDefault();
        addToCart(this.dataset.productId);
    }

    function handleCartActions(e) {
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
            if (confirm('Очистить всю корзину?')) {
                clearCart();
            }
        }
    }
}

let lastAdded = {};

async function addToCart(productId) {
    const now = Date.now();
    if (lastAdded[productId] && now - lastAdded[productId] < 1000) {
        return;
    }
    lastAdded[productId] = now;

    const button = document.querySelector(`.add-to-cart-btn[data-product-id="${productId}"]`);
    if (button.disabled) return;
    button.disabled = true;

    try {
        let quantity = 1;
        const quantityInput = button.closest('.product-card')?.querySelector('.quantity-input');
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
            const cartContainer = document.getElementById('cart-container');
            if (cartContainer) {
                cartContainer.innerHTML = data.cart_html;
            }

            updateCartBadge(data.total_items);

            const headerTotalElement = document.getElementById('header-cart-total');
            if (headerTotalElement) {
                headerTotalElement.textContent = `${data.total_sum} ₽`;
            }

            showToast('Товар добавлен в корзину');
        } else {
            alert(data.message || 'Ошибка при добавлении товара в корзину');
        }
    } catch (error) {
        console.error('Add to cart failed:', error);
        alert(error.message !== 'HTTP error! Status: 400' ? `Ошибка: ${error.message}` : 'Товар отсутствует на складе');
    } finally {
        button.disabled = false;
    }
}

async function updateCart(basketId, action) {
  const cartItem = document.querySelector(`.cart-item[data-basket-id="${basketId}"]`);
    if (!cartItem) {
        console.error('Cart item not found');
        return;
    }

    const button = document.querySelector(`.quantity-btn[data-basket-id="${basketId}"][data-action="${action}"]`);
    if (button.disabled) return;
    button.disabled = true;

    const quantityElement = cartItem.querySelector('.quantity-value');
    const sumElement = cartItem.querySelector('.item-details');
    const totalElement = document.querySelector('.total-price');
    const headerTotalElement = document.getElementById('header-cart-total');

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
                throw new Error(`HTTP error! Status: ${response.status}: ${data.message || 'Unknown error'}`);
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
            if (headerTotalElement) headerTotalElement.textContent = `${data.total_sum} ₽`;
        } else if (data.status === 'removed') {
            cartItem.style.transition = 'opacity 0.3s';
            cartItem.style.opacity = '0';
            setTimeout(() => cartItem.remove(), 300);
            if (totalElement) totalElement.textContent = `${data.total_sum} ₽`;
            if (headerTotalElement) headerTotalElement.textContent = `${data.total_sum} ₽`;
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
    } finally {
        button.disabled = false; // Разблокируем кнопку
    }
}

async function clearCart() {
    try {
        const response = await fetch('/products/clear_basket_ajax/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.message || `HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'success' || data.status === 'empty') {
            const cartContainer = document.getElementById('cart-container');
            if (cartContainer) {
                cartContainer.innerHTML = data.cart_html || renderEmptyCart();
            }
            updateCartBadge(0);
            const headerTotalElement = document.getElementById('header-cart-total');
            if (headerTotalElement) {
                headerTotalElement.textContent = 'Корзина пуста';
            }
            showToast('Корзина очищена');
        } else {
            alert(data.message || 'Ошибка при очистке корзины');
        }
    } catch (error) {
        console.error('Clear cart failed:', error);
        alert(`Ошибка при очистке корзины: ${error.message}`);
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