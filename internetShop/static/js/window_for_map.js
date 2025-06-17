// Доп. окно для карты
const output = document.getElementById('output');
const mapModal = document.getElementById('map-modal');

// Обработчик для вывода в базовом шаблоне
if (output) {
    output.addEventListener('click', function() {
        mapModal.style.display = 'flex';
    });
}

// Обработчик для поля адреса в форме заказа
const addressInput = document.getElementById('id_address');
if (addressInput) {
    addressInput.addEventListener('click', function() {
        mapModal.style.display = 'flex';
    });
}

function closeMap() {
    mapModal.style.display = 'none';
}