document.addEventListener('DOMContentLoaded', function() {
    const catalogBtn = document.getElementById('catalogBtn');
    const categoriesMenu = document.getElementById('categoriesMenu');
    const productMenu = document.getElementById('productMenu');
    const containerMenu = document.getElementById('containerMenu');
    const categoryItems = document.querySelectorAll('.category-item');

    // Открытие/закрытие меню
    catalogBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        categoriesMenu.classList.toggle('active');
        productMenu.classList.toggle('active');
        containerMenu.classList.toggle('active');
    });

    // Обработка клика на категорию
    categoryItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const categoryId = this.getAttribute('data-category-id');
            window.location.href = `/products/category/${categoryId}/`;
        });

        item.addEventListener('mouseenter', function() {
            const categoryId = this.getAttribute('data-category-id');

            fetch(`/api/products/?category_id=${categoryId}`)
                .then(response => response.json())
                .then(products => {
                    productMenu.innerHTML = '';

                    if (products.length > 0) {
                        products.forEach(product => {
                            const productElement = document.createElement('a');
                            productElement.href = `/products/${product.id}/`;
                            productElement.className = 'product-item';
                            productElement.textContent = product.name;
                            productMenu.appendChild(productElement);
                        });
                    } else {
                        const noProducts = document.createElement('span');
                        noProducts.className = 'product-item';
                        noProducts.textContent = 'Нет товаров';
                        productMenu.appendChild(noProducts);
                    }

                    if (!productMenu.classList.contains('active')) {
                        productMenu.classList.add('active');
                    }
                });
        });
    });

    // Закрытие при клике вне меню
    document.addEventListener('click', function() {
        categoriesMenu.classList.remove('active');
        productMenu.classList.remove('active');
        containerMenu.classList.remove('active');
    });

    // Предотвращаем закрытие при клике внутри меню
    categoriesMenu.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    productMenu.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    containerMenu.addEventListener('click', function(e) {
        e.stopPropagation();
    });
});