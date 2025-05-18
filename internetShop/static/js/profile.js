   document.querySelectorAll('.profile-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                // Удаляем активный класс у всех табов и контента
                document.querySelectorAll('.profile-tab, .tab-content').forEach(el => {
                    el.classList.remove('active');
                });

                // Добавляем активный класс текущему табу и соответствующему контенту
                tab.classList.add('active');
                document.getElementById(tab.dataset.tab).classList.add('active');
            });
        });

        // Скрипт для загрузки фото профиля
        document.getElementById('photoUpload').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('fileName').textContent = file.name;

                // Превью загруженного изображения
                const reader = new FileReader();
                reader.onload = function(event) {
                    document.getElementById('profilePhoto').src = event.target.result;
                }
                reader.readAsDataURL(file);
            }
        });