document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]')?.value;

    if (!searchInput || !searchResults) {
        console.error('Элементы поиска не найдены: search-input или search-results отсутствуют');
        return;
    }

    let debounceTimeout;

    searchInput.addEventListener('input', function () {
        clearTimeout(debounceTimeout);
        const query = this.value.trim();

        if (query.length < 2) {
            searchResults.classList.add('hidden');
            searchResults.innerHTML = '';
            return;
        }

        debounceTimeout = setTimeout(() => {
            fetch(`/products/search/?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken || ''
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                searchResults.innerHTML = '';

                if (!data.results || data.results.length === 0) {
                    const noResults = document.createElement('div');
                    noResults.className = 'search-result-item no-results';
                    noResults.textContent = 'Ничего не найдено';
                    searchResults.appendChild(noResults);
                } else {
                    data.results.forEach(item => {
                        const itemDiv = document.createElement('div');
                        itemDiv.className = `search-result-item ${item.type}-item`;

                        const imageSrc = item.image || '/static/images/placeholder.png';
                        const displayName = item.type === 'category' ? `Категория: ${item.name}` : item.name;

                        itemDiv.innerHTML = `
                            ${item.type === 'product' ? `<img src="${imageSrc}" class="search-result-image" alt="${item.name}">` : ''}
                            <span class="search-result-name">${displayName}</span>
                        `;

                        itemDiv.addEventListener('click', () => {
                            if (item.type === 'product') {
                                window.location.href = `/products/${item.id}/`;
                            } else {
                                window.location.href = `/products/category/${item.id}/`;
                            }
                        });

                        searchResults.appendChild(itemDiv);
                    });
                }
                searchResults.classList.remove('hidden');
            })
            .catch(error => {
                console.error('Ошибка поиска:', error);
                searchResults.innerHTML = '<div class="search-result-item no-results">Ошибка при поиске</div>';
                searchResults.classList.remove('hidden');
            });
        }, 300);
    });

    document.addEventListener('click', function (event) {
        if (!searchInput.contains(event.target) && !searchResults.contains(event.target)) {
            searchResults.classList.add('hidden');
            searchResults.innerHTML = '';
        }
    });
});