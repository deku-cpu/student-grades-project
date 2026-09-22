// --- Переключатель видимости пароля ---
const passwordInput = document.getElementById('password');
const passwordConfirmInput = document.getElementById('passwordConfirm');
const eyeTogglePassword = document.getElementById('eyeTogglePassword');

const passwordConfirmToggle = document.getElementById('passwordConfirmToggle');

 
const eyeIcon = document.getElementById('eyeIcon');

const eyeOpenPath = `
  <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7Z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.6"/>
`;
const eyeClosedPath = `
  <path d="M3 3l18 18" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M10.6 5.2A11.6 11.6 0 0 1 12 5c7 0 11 7 11 7a13.9 13.9 0 0 1-3.4 4.1M6.6 6.6C3.4 8.6 1 12 1 12s4 7 11 7c1.4 0 2.7-.2 3.9-.7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
`;

passwordInput.addEventListener('input', () => { 
 
  const password = passwordInput.value; 
  const field = passwordInput.closest('.field');        // родитель .field
  const status = field.querySelector('.password--status');
  const len = password.length;

  if (len < 8){
    status.textContent = 'Нужно 8 и более символов';
    status.style.display = 'block';  // показать
    return;
  }
  status.style.display = 'none';  // показать

});



eyeTogglePassword.addEventListener('click', () => {
  changeInputView(passwordInput);
  eyeTogglePassword.setAttribute('aria-label', isPassword ? 'Скрыть пароль' : 'Показать пароль');
});


passwordConfirmToggle.addEventListener('click', () => {
  changeInputView(passwordConfirmInput);
  passwordConfirmToggle.setAttribute('aria-label', isPassword ? 'Скрыть пароль' : 'Показать пароль');
});


function changeInputView(input) {
  const isPassword = input.type === 'password';
  input.type = isPassword ? 'text' : 'password';
}

// --- Подсветка карточки, следующая за курсором (hover-эффект) ---
const card = document.getElementById('card');
const glow = document.getElementById('cardGlow');

card.addEventListener('mousemove', (e) => {
  const rect = card.getBoundingClientRect();
  const x = ((e.clientX - rect.left) / rect.width) * 100;
  const y = ((e.clientY - rect.top) / rect.height) * 100;
  glow.style.setProperty('--mx', `${x}%`);
  glow.style.setProperty('--my', `${y}%`);
});

// Подсвечиваем карточку и когда фокус внутри неё (клавиатура, без мыши)
const focusableFields = card.querySelectorAll('input');
focusableFields.forEach((field) => {
  field.addEventListener('focus', () => card.classList.add('focus-within'));
  field.addEventListener('blur', () => card.classList.remove('focus-within'));
});

// --- Заглушки для формы (пока без бэкенда) ---
const form = document.getElementById('loginForm');
form.addEventListener('submit', (e) => {
  e.preventDefault();
  console.log('TODO: отправка запроса на Django-бэкенд', {
    email: document.getElementById('email').value,
    password: passwordInput.value,
    remember: document.getElementById('remember').checked,
  });
});
/*
document.getElementById('registerBtn').addEventListener('click', () => {
  console.log('TODO: переход на страницу регистрации');
});
*/
