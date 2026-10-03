//словари
const FORM_LABELS = {
    'full-time': 'Очная',
    'part-time': 'Заочная',
    'distance_learning': 'Дистанционная'
};

const testProfile = {
    id: 2,
    role: 'student',
    login: 'oleg',
    fullName: 'Тиньков Олег Юрьевич',
    group: 'ПИЭ-228-2',
    yearOfStudy: 3,
    specialty: 'Прикладная информатика в экономике',
    form: 'full-time',
    admissionYear: 2023,
    email: 'govno@example.com',
    phone: '+7 (777) 777-77-77'
};

//инициалы для аватарки
function getInitials(fullName) {
    const parts = fullName.split(' ').filter(Boolean);
    return ((parts[0]?.[0] ?? '') + (parts[1]?.[0] ?? '')).toUpperCase();
}


document.getElementById('profileName').textContent = testProfile.fullName;
document.getElementById('profileGroup').textContent = testProfile.group;

document.getElementById('profileLogin').textContent = testProfile.login;
document.getElementById('profileYear').textContent = testProfile.yearOfStudy + ' курс';
document.getElementById('profileSpecialty').textContent = testProfile.specialty;
document.getElementById('profileForm').textContent = FORM_LABELS[testProfile.form] ?? testProfile.form;
document.getElementById('profileAdmissionYear').textContent = testProfile.admissionYear;
document.getElementById('profileEmail').textContent = testProfile.email;
document.getElementById('profilePhone').textContent = testProfile.phone;

document.querySelector('.profile-card__avatar').textContent = getInitials(testProfile.fullName);