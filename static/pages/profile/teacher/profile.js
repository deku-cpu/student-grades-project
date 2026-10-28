const testProfile = {
    id: 1,
    role: 'teacher',
    login: 'yapidoras',
    fullName: 'Иванов Иван Иванович',
    position: 'Доцент',
    department: 'Кафедра информатики',
    email: 'zalupa@example.com',
    phone: '+7 (228) 067-14-88',
    subjects: ['Математика', 'Программирование', 'Базы данных']
};

//инициалы для аватарки
function getInitials(fullName) {
    const parts = fullName.split(' ').filter(Boolean);
    return ((parts[0]?.[0] ?? '') + (parts[1]?.[0] ?? '')).toUpperCase();
}

document.getElementById('profileName').textContent = testProfile.fullName;
document.getElementById('profilePosition').textContent = testProfile.position;
document.getElementById('profileLogin').textContent = testProfile.login;
document.getElementById('profileDepartment').textContent = testProfile.department;
document.getElementById('profileEmail').textContent = testProfile.email;
document.getElementById('profilePhone').textContent = testProfile.phone;

document.querySelector('.profile-card__avatar').textContent = getInitials(testProfile.fullName);

document.getElementById('profileSubjects').innerHTML = testProfile.subjects
    .map(s => `<span class="profile-tag">${s}</span>`)
    .join('');