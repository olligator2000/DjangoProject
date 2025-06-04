//document.addEventListener('DOMContentLoaded', initCart);
//
//function initCart() {
//    const isAuthenticated = {{ request.user.is_authenticated|lower }};
//    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
//
//    if (!isAuthenticated) {
//        document.querySelectorAll('.add-to-cart-btn, .quantity-btn, .clear-cart-btn').forEach(btn => {
//            btn.addEventListener('click', () => {
//                alert('Для управления корзиной войдите в систему');
//                window.location.href = "{% url 'users:login' %}?next={{ request.path }}";
//            });
//        });
//        return;
//    }
//
//    if (!csrfToken) {
//        console.error('CSRF token not found');
//        alert('Ошибка: CSRF-токен не найден. Перезагрузите страницу.');
//        return;
//    }
//
//    setupHandlers();
//}
//
//function setupHandlers() {
//    // Обработчик для добавления в корзину
//    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
//        btn.addEventListener('click', () => addToCart(btn.dataset.productId));
//    });
//
//    // Делегирование событий для кнопок "+" и "−" и очистки корзины
//    document.addEventListener('click', (e) => {
//        if (e.target.classList.contains('quantity-btn')) {
//            e.preventDefault();
//            const { basketId, action } = e.target.dataset;
//            if (!basketId || !action) {
//                console.error('Missing basket ID or action');
//                return;
//            }
//            updateCart(basketId, action);
//        } else if (e.target.classList.contains('clear-cart-btn')) {
//            e.preventDefault();
//            if (confirm('Очистить всю корзину?')) clearCart();
//        }
//    });
//}
//
//async function addToCart(productId) {
//    try {
//        const response = await fetch(`/products/add_to_cart_ajax/${productId}/`, {
//            method: 'POST',
//            headers: { 'X-CSRFToken': getCSRFToken(), 'Content-Type': 'application/json' }
//        });
//
//        if (!response.ok) {
//            const data = await response.json();
//            if (data.message === 'Товар отсутствует на складе') {
//                alert('Товар отсутствует на складе');
//            } else {
//                throw new Error(`HTTP error! Status: ${response.status}`);
//            }
//            return;
//        }
//
//        const data = await response.json();
//
//        if (data.status === 'success') {
//            document.getElementById('cart-container').innerHTML = data.cart_html;
//            updateCartBadge(data.total_items);
//        } else {
//            alert(data.message || 'Ошибка при добавлении товара в корзину');
//        }
//    } catch (error) {
//        console.error('Add to cart failed:', error);
//        alert(error.message !== 'HTTP error! Status: 400' ? `Ошибка: ${error.message}` : 'Товар отсутствует на складе');
//    }
//}
//
//async function updateCart(basketId, action) {
//    const cartItem = document.querySelector(`.cart-item[data-basket-id="${basketId}"]`);
//    if (!cartItem) {
//        console.error('Cart item not found');
//        return;
//    }
//
//    const quantityElement = cartItem.querySelector('.quantity-value');
//    const sumElement = cartItem.querySelector('.item-details');
//    const totalElement = document.querySelector('.total-price');
//
//    const originalQuantity = quantityElement.textContent;
//    const originalSum = sumElement.textContent;
//
//
//    try {
//        const response = await fetch(`/products/update_basket_ajax/${basketId}/${action}/`, {
//            method: 'POST',
//            headers: { 'X-CSRFToken': getCSRFToken(), 'Content-Type': 'application/json' }
//        });
//
//        if (!response.ok) {
//            const data = await response.json();
//            if (response.status === 400 && data.message && data.message.startsWith('Недостаточно товара на складе. Доступно: ')) {
//                const availableQuantity = data.message.split(' ').pop();
//                alert(`На складе всего ${availableQuantity} штук`);
//            } else {
//                throw new Error(`HTTP error! Status: ${response.status}`);
//            }
//            quantityElement.textContent = originalQuantity;
//            sumElement.textContent = originalSum;
//            return;
//        }
//
//        const data = await response.json();
//
//        if (data.status === 'success') {
//            quantityElement.textContent = data.quantity;
//            sumElement.textContent = `${data.sum} ₽`;
//            if (totalElement) totalElement.textContent = `${data.total_sum} ₽`;
//        } else if (data.status === 'removed') {
//            cartItem.style.transition = 'opacity 0.3s';
//            cartItem.style.opacity = '0';
//            setTimeout(() => cartItem.remove(), 300);
//            if (totalElement) totalElement.textContent = `${data.total_sum} ₽`;
//            if (data.total_sum === 0) {
//                document.querySelector('.cart-items-container').innerHTML = '<div class="basket-pusto">В корзине нет товаров</div>';
//            }
//        } else {
//            quantityElement.textContent = originalQuantity;
//            sumElement.textContent = originalSum;
//            alert(data.message || 'Ошибка при обновлении корзины');
//        }
//    } catch (error) {
//        console.error('Update cart failed:', error);
//        quantityElement.textContent = originalQuantity;
//        sumElement.textContent = originalSum;
//        alert(`Ошибка: ${error.message}`);
//    }
//}
//
//async function clearCart() {
//    try {
//        const response = await fetch('/products/clear_basket_ajax/', {
//            method: 'POST',
//            headers: { 'X-CSRFToken': getCSRFToken(), 'Content-Type': 'application/json' }
//        });
//
//        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
//        const data = await response.json();
//
//        if (data.status === 'success' || data.status === 'empty') {
//            document.getElementById('cart-container').innerHTML = data.cart_html || renderEmptyCart();
//            updateCartBadge(0);
//        } else {
//            alert(data.message || 'Ошибка при очистке корзины');
//        }
//    } catch (error) {
//        console.error('Clear cart failed:', error);
//        alert(`Ошибка: ${error.message}`);
//    }
//}
//
//function getCSRFToken() {
//    return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
//}
//
//function updateCartBadge(count) {
//    const badge = document.querySelector('.cart-badge');
//    if (badge) {
//        badge.textContent = count;
//        badge.style.display = count > 0 ? 'block' : 'none';
//    }
//}
//
//function renderEmptyCart() {
//    return `
//        <div class="cart-sidebar">
//            <div class="cart-header">
//                <h2 class="cart-title">Корзина</h2>
//            </div>
//            <div class="basket-pusto">В корзине нет товаров</div>
//        </div>
//    `;
//}