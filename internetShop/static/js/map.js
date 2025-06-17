ymaps.ready(init);

function init() {
    var geolocation = ymaps.geolocation,
        myPlacemark,
        myMap = new ymaps.Map('map', {
            center: [55.751574, 37.573856], // Координаты по умолчанию (Москва)
            zoom: 15
        }, {
            searchControlProvider: 'yandex#search',
            suppressMapOpenBlock: true
        });

    // Функция для обновления адреса
    function updateAddressOutput(address, details) {
        const output = document.getElementById('output');
        if (output) output.textContent = address;

        const addressInput = document.getElementById('id_address');
        const apartmentInput = document.getElementById('id_apartment_office');
        const entranceInput = document.getElementById('id_entrance');

        if (addressInput) addressInput.value = address;
        if (apartmentInput && details.apartment) apartmentInput.value = details.apartment;
        if (entranceInput && details.entrance) entranceInput.value = details.entrance;
    }

    // Основная функция определения адреса
    function updateAddress(coords) {
        ymaps.geocode(coords, {
            kind: 'house',
            results: 1
        }).then(function(res) {
            var firstGeoObject = res.geoObjects.get(0);
            if (!firstGeoObject) {
                updateAddressOutput('Адрес не определен', {});
                return;
            }

            // Обновляем метку
            if (myPlacemark) myMap.geoObjects.remove(myPlacemark);

            myPlacemark = new ymaps.Placemark(coords, {}, {
                iconLayout: 'default#image',
                iconImageHref: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"></svg>',
                iconImageSize: [32, 32],
                iconImageOffset: [-16, -32],
                draggable: false
            });
            myMap.geoObjects.add(myPlacemark);

            // Парсим адрес
            var fullAddress = firstGeoObject.getAddressLine();
            var addressDetails = {};
            firstGeoObject.getAddressLine().split(', ').forEach(component => {
                if (component.toLowerCase().includes('кв.')) {
                    addressDetails.apartment = component.replace('кв.', '').trim();
                } else if (component.toLowerCase().includes('подъезд')) {
                    addressDetails.entrance = component.replace('подъезд', '').trim();
                }
            });

            updateAddressOutput(fullAddress, addressDetails);
        }).catch(console.error);
    }

    // Пытаемся получить геолокацию
    geolocation.get({
        provider: 'browser',
        mapStateAutoApply: true,
        timeout: 5000 // Таймаут 5 секунд
    }).then(function(result) {
        myMap.setCenter(result.geoObjects.get(0).geometry.getCoordinates(), 17);
        updateAddress(result.geoObjects.get(0).geometry.getCoordinates());
    }).catch(function(error) {
        // Если геолокация запрещена или недоступна
        console.log('Геолокация недоступна, используем координаты по умолчанию');

        // Используем координаты по умолчанию (Москва)
        var defaultCoords = [55.751574, 37.573856];
        myMap.setCenter(defaultCoords, 15);
        updateAddress(defaultCoords);

        // Можно также предложить пользователю выбрать местоположение вручную
        // через поиск или перемещение карты
    });

    // Обработчики изменений карты
    var updateTimer;
    myMap.events.add(['boundschange', 'actionend'], function(e) {
        if (e.get('newZoom') < 14) return;
        clearTimeout(updateTimer);
        updateTimer = setTimeout(() => updateAddress(myMap.getCenter()), 300);
    });

    myMap.events.add('click', function(e) {
        myMap.panTo(e.get('coords'), { flying: true, duration: 300 });
    });
}