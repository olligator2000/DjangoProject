document.addEventListener('DOMContentLoaded', initCart);

function initCart() {
    const isAuthenticated = window.isAuthenticated;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    if (!isAuthenticated) {
        bindUnauthenticatedHandlers();
        return;
    }

    if (!csrfToken) {
        console.error('CSRF token not found');
        showToast('Ошибка: CSRF-токен не найден. Перезагрузите страницу.', 'error');
        return;
    }

    setupHandlers();
    syncCartState();
}

function bindUnauthenticatedHandlers() {
    document.querySelectorAll('.add-to-cart-btn, .quantity-btn, .clear-cart-btn').forEach(btn => {
        btn.removeEventListener('click', handleAuthRedirect);
        btn.addEventListener('click', handleAuthRedirect);
    });
}

function handleAuthRedirect(e) {
    e.preventDefault();
    showToast('Для управления корзиной войдите в систему', 'info');
    window.location.href = window.loginUrl;
}

function setupHandlers() {
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.removeEventListener('click', handleAddToCart);
        btn.addEventListener('click', handleAddToCart);
    });

    document.querySelectorAll('.quantity-btn, .clear-cart-btn').forEach(btn => {
        btn.removeEventListener('click', handleCartActions);
        btn.addEventListener('click', handleCartActions);
    });

    function handleAddToCart(e) {
        e.preventDefault();
        addToCart(this.dataset.productId);
    }

    function handleCartActions(e) {
        e.preventDefault();
        if (e.target.classList.contains('quantity-btn')) {
            const basketId = e.target.dataset.basketId;
            const action = e.target.dataset.action;
            if (!basketId || !action) {
                console.error('Missing basket ID or action', e.target.dataset);
                showToast('Ошибка: неверные данные корзины', 'error');
                return;
            }
            updateCart(basketId, action);
        } else if (e.target.classList.contains('clear-cart-btn')) {
            showClearCartModal();
        }
    }
}

function showClearCartModal() {
    // Удаляем существующее модальное окно, если есть
    const existingModal = document.querySelector('.clear-cart-modal');
    if (existingModal) existingModal.remove();

    // Создаем модальное окно
    const modal = document.createElement('div');
    modal.className = 'clear-cart-modal';
    modal.innerHTML = `
        <div class="clear-cart-modal-content">
            <h3>Очистить всю корзину?</h3>
            <div class="clear-cart-modal-buttons">
                <button class="clear-cart-confirm-btn">Да</button>
                <button class="clear-cart-cancel-btn">Нет</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // Обработчики для кнопок
    const confirmBtn = modal.querySelector('.clear-cart-confirm-btn');
    const cancelBtn = modal.querySelector('.clear-cart-cancel-btn');

    confirmBtn.addEventListener('click', () => {
        clearCart();
        modal.remove();
    });

    cancelBtn.addEventListener('click', () => {
        modal.remove();
    });

    // Закрытие при клике на фон
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
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
        const quantityInput = button.closest('.product-card, .custom-product-card')?.querySelector('.quantity-input');
        if (quantityInput) {
            quantity = parseInt(quantityInput.value) || 1;
        }

        const response = await fetch(`/products/add_to_cart_ajax/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ quantity })
        });

        if (!response.ok) {
            const data = await response.json();
            if (data.message === 'Товар отсутствует на складе') {
                showToast('Товара нет на складе', 'info');
            } else {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return;
        }

        const data = await response.json();

        if (data.status === 'success') {
            updateCartDisplay(data);
            syncCartState();
        } else {
            showToast(data.message || 'Ошибка при добавлении товара в корзину', 'error');
        }
    } catch (error) {
        console.error('Add to cart failed:', error);
        showToast('Товара нет на складе', 'info');
    } finally {
        button.disabled = false;
    }
}

async function updateCart(basketId, action) {
    const cartItem = document.querySelector(`.cart-item[data-basket-id="${basketId}"], .order-item[data-basket-id="${basketId}"]`);
    if (!cartItem) {
        console.error('Cart item not found for basketId:', basketId);
        showToast('Элемент корзины не найден', 'error');
        return;
    }

    const button = document.querySelector(`.quantity-btn[data-basket-id="${basketId}"][data-action="${action}"]`);
    if (button.disabled) return;
    button.disabled = true;

    const quantityElement = cartItem.querySelector('.quantity-value');
    const sumElement = cartItem.querySelector('.item-price');
    const originalQuantity = quantityElement.textContent;
    const originalSum = sumElement ? sumElement.getAttribute('data-item-sum') || sumElement.textContent.match(/\d+/)?.[0] : '0';

    try {
        const response = await fetch(`/products/update_basket_ajax/${basketId}/${action}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken(), 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            const data = await response.json();
            if (response.status === 400 && data.message && data.message.startsWith('Недостаточно товара на складе. Доступно: ')) {
                const availableQuantity = data.message.split(' ').pop();
                showToast(`Максимум для заказа ${availableQuantity} шт.`, 'info');
            } else {
                throw new Error(`HTTP error! Status: ${response.status}: ${data.message || 'Unknown error'}`);
            }
            if (sumElement) {
                sumElement.textContent = `${originalSum} ₽`;
                sumElement.setAttribute('data-item-sum', originalSum);
            }
            return;
        }

        const data = await response.json();

        if (data.status === 'success' || data.status === 'removed') {
            updateCartDisplay(data);
            if (data.status === 'success') {
                quantityElement.textContent = data.quantity;
                if (sumElement) {
                    sumElement.textContent = `${data.sum} ₽`;
                    sumElement.setAttribute('data-item-sum', data.sum);
                }
            } else if (data.status === 'removed') {
                cartItem.style.transition = 'opacity 0.3s';
                cartItem.style.opacity = '0';
                setTimeout(() => cartItem.remove(), 300);

                const remainingItems = document.querySelectorAll('.cart-item, .order-item').length - 1;
                if (remainingItems <= 0 || data.total_sum === 0) {
                    const emptyCartHtml = '<div class="basket-pusto">В корзине нет товаров</div>';
                    const cartContainer = document.querySelector('.cart-items-container, .order-items');
                    if (cartContainer) cartContainer.innerHTML = emptyCartHtml;
                    updateAllTotalElements(0, true);
                }
            }
            syncCartState();
        } else {
            quantityElement.textContent = originalQuantity;
            if (sumElement) {
                sumElement.textContent = `${originalSum} ₽`;
                sumElement.setAttribute('data-item-sum', originalSum);
            }
            showToast(data.message || 'Ошибка при обновлении корзины', 'error');
        }
    } catch (error) {
        console.error('Update cart failed:', error);
        quantityElement.textContent = originalQuantity;
        if (sumElement) {
            sumElement.textContent = `${originalSum} ₽`;
            sumElement.setAttribute('data-item-sum', originalSum);
        }
        showToast(`Ошибка: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
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
            // Проверяем, находится ли пользователь на zakaz_end.html
            if (window.location.pathname.includes('/zakaz_end/')) {
                // Обновляем только .order-items, не трогая #cart-container
                const orderItems = document.querySelector('.order-items');
                if (orderItems) {
                    orderItems.innerHTML = '<div class="basket-pusto">В корзине нет товаров</div>';
                }
                updateAllTotalElements(0, true);
            } else {
                // Для других страниц обновляем #cart-container
                const cartContainer = document.getElementById('cart-container') || document.querySelector('.order-items');
                if (cartContainer) {
                    cartContainer.innerHTML = data.cart_html || renderEmptyCart();
                }
                updateCartDisplay(data);
            }
            syncCartState();
        } else {
            showToast(data.message || 'Ошибка при очистке корзины', 'error');
        }
    } catch (error) {
        console.error('Clear cart failed:', error);
        showToast(`Ошибка при очистке корзины: ${error.message}`, 'error');
    }
}

async function syncCartState() {
    try {
        const response = await fetch('/products/get_cart_state/', {
            method: 'GET',
            headers: { 'X-CSRFToken': getCSRFToken() }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        updateCartDisplay(data);
    } catch (error) {
        console.error('Sync cart state failed:', error);
        showToast('Ошибка синхронизации корзины', 'error');
    }
}

function updateCartDisplay(data) {
    updateCartBadge(data.total_items || 0);
    updateAllTotalElements(data.total_sum || 0, data.total_items === 0);
    // Обновляем #cart-container только если не на zakaz_end.html
    if (!window.location.pathname.includes('/zakaz_end/')) {
        const cartContainer = document.getElementById('cart-container');
        if (cartContainer && data.cart_html) {
            cartContainer.innerHTML = data.cart_html;
            setupHandlers(); // Повторная привязка обработчиков
        }
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

function updateAllTotalElements(totalSum, isEmpty = false) {
    document.querySelectorAll(`
        .total-price,
        #header-cart-total,
        .cart-total,
        .total-row .total-price,
        .payment-details .total-price
    `).forEach(el => {
        el.textContent = isEmpty ? 'Корзина пуста' : `${totalSum} ₽`;
    });
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

function showToast(message, type = 'info') {
    // На zakaz_end.html показываем только уведомления типа 'info'
    if (window.location.pathname.includes('/zakaz_end/') && type !== 'info') {
        return;
    }

    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
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