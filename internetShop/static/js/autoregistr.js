document.addEventListener('DOMContentLoaded', function() {
  const loginButton = document.getElementById('loginButton');
  const authModal = document.getElementById('authModal');
  const closeModal = document.querySelector('.close-modal');
  const loginBlock = document.getElementById('loginBlock');
  const registerBlock = document.getElementById('registerBlock');
  const userBlock = document.getElementById('userBlock');
  const showRegister = document.getElementById('showRegister');
  const showLogin = document.getElementById('showLogin');
  const logoutBtn = document.getElementById('logoutBtn');
  const usernameDisplay = document.getElementById('usernameDisplay');
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');

  // Открытие модального окна
  loginButton.addEventListener('click', function() {
    authModal.style.display = 'block';
    loginBlock.style.display = 'block';
    registerBlock.style.display = 'none';
  });

  // Закрытие модального окна
  closeModal.addEventListener('click', function() {
    authModal.style.display = 'none';
  });

  // Переключение между формами
  showRegister.addEventListener('click', function(e) {
    e.preventDefault();
    loginBlock.style.display = 'none';
    registerBlock.style.display = 'block';
  });

  showLogin.addEventListener('click', function(e) {
    e.preventDefault();
    registerBlock.style.display = 'none';
    loginBlock.style.display = 'block';
  });

  // Обработка входа
  loginForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const username = this.querySelector('input[type="text"]').value;
    // Здесь должна быть реальная проверка логина/пароля
    authModal.style.display = 'none';
    loginButton.style.display = 'none';
    userBlock.style.display = 'flex';
    usernameDisplay.textContent = username;
    localStorage.setItem('currentUser', username);
  });

  // Обработка регистрации
  registerForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const username = this.querySelector('input[placeholder="Введите имя пользователя"]').value;
    // Здесь должна быть реальная регистрация
    authModal.style.display = 'none';
    loginButton.style.display = 'none';
    userBlock.style.display = 'flex';
    usernameDisplay.textContent = username;
    localStorage.setItem('currentUser', username);
  });

  // Выход из системы
  logoutBtn.addEventListener('click', function() {
    userBlock.style.display = 'none';
    loginButton.style.display = 'block';
    localStorage.removeItem('currentUser');
  });

  // Проверка авторизации при загрузке
  const currentUser = localStorage.getItem('currentUser');
  if (currentUser) {
    loginButton.style.display = 'none';
    userBlock.style.display = 'flex';
    usernameDisplay.textContent = currentUser;
  }

});