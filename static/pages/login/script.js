// --- Переключатель видимости пароля ---
const passwordInput = document.getElementById('password');
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

const eyeToggle = document.getElementById('eyeToggle');

eyeToggle.addEventListener('click', () => {
  changeInputView(passwordInput);
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

const form = document.getElementById('loginForm');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const email = document.getElementById('email').value;
  const password = passwordInput.value;

  const response = await fetch('/api/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: email, password: password }),
    credentials: 'include',
  });

  const data = await response.json();

  localStorage.setItem('role', data.role);

  if (response.ok) {
    if (data.role === 'student') {
      window.location.href = '/static/pages/grades/roles/student/diary/diary.html';
    } else if (data.role === 'teacher') {
      window.location.href = '/static/pages/grades/roles/teacher/journal/journal.html';
    } else if (data.role === 'deans_office') {
      window.location.href = '/static/pages/grades/roles/dekan/journal/journal.html';
    } else {
      window.location.href = '/admin/';
    }
  } else {
    alert(data.error);
  }
});