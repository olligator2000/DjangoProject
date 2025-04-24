document.addEventListener('DOMContentLoaded', function() {
    const catalogBtn = document.getElementById('catalogBtn');
    const categoriesMenu = document.getElementById('categoriesMenu');

    // Открытие/закрытие меню
    catalogBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        categoriesMenu.classList.toggle('active');
    });

    // Закрытие при клике вне меню
    document.addEventListener('click', function() {
        categoriesMenu.classList.remove('active');
    });

    // Предотвращаем закрытие при клике внутри меню
    categoriesMenu.addEventListener('click', function(e) {
        e.stopPropagation();
    });

});