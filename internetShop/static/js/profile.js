// Превью загружаемого фото
document.getElementById('up-photo-input').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const placeholder = document.querySelector('.up-photo-placeholder');
            placeholder.innerHTML = `<img src="${event.target.result}" style="width:100%;height:100%;object-fit:cover;">`;
        };
        reader.readAsDataURL(file);
    }
});