document.addEventListener('DOMContentLoaded', () => {
    const API_URL = '/api/disciplines/';
    
    const tbody = document.getElementById('disciplines-body');
    const modal = document.getElementById('editingModal');
    const form = document.getElementById('editFormTag');
    
    // Фильтры
    const filterSearch = document.getElementById('filterSearch');
    const filterControlForm = document.getElementById('filterControlForm');

    // Элементы формы
    const editId = document.getElementById('editId');
    const editName = document.getElementById('editName');
    const editDescription = document.getElementById('editDescription');
    const editHoursLecture = document.getElementById('editHoursLecture');
    const editHoursPractice = document.getElementById('editHoursPractice');
    const editHoursLab = document.getElementById('editHoursLab');
    const editControlForm = document.getElementById('editControlForm');

    // Загрузка данных
    async function loadDisciplines() {
        const search = filterSearch.value;
        const control = filterControlForm.value;
        
        let url = new URL(window.location.origin + API_URL);
        if (search) url.searchParams.append('search', search);
        if (control) url.searchParams.append('control_form', control);

        try {
            const response = await fetch(url);
            const data = await response.json();
            renderTable(data);
        } catch (error) {
            console.error('Ошибка загрузки:', error);
        }
    }

    // Отрисовка таблицы
    function renderTable(data) {
        tbody.innerHTML = '';
        
        data.forEach(item => {
            const tr = document.createElement('tr');
            
            // Находим текстовое значение для формы контроля из селекта
            const controlOption = filterControlForm.querySelector(`option[value="${item.control_form}"]`);
            const controlText = controlOption ? controlOption.textContent : item.control_form;

            tr.innerHTML = `
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.hours_lecture}</td>
                <td>${item.hours_practice}</td>
                <td>${item.hours_lab}</td>
                <td>${controlText}</td>
                <td>
                    <button class="btn btn--secondary" onclick="openEditModal(${item.id})">Ред.</button>
                    <button class="btn btn--danger" onclick="deleteDiscipline(${item.id})">Удал.</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Открытие модалки для добавления
    document.getElementById('addDisciplineBtn').addEventListener('click', () => {
        form.reset();
        editId.value = '';
        modal.classList.remove('hidden');
    });

    // Открытие модалки для редактирования (глобальная функция для onclick в таблице)
    window.openEditModal = async (id) => {
        try {
            // Так как у нас нет GET по ID, берем данные из общего списка (или запрашиваем всё и ищем)
            // В идеале лучше сделать GET запрос к /api/disciplines/{id}/, но используем то, что есть
            const response = await fetch(API_URL);
            const data = await response.json();
            const item = data.find(d => d.id === id);

            if (item) {
                editId.value = item.id;
                editName.value = item.name;
                editDescription.value = item.description;
                editHoursLecture.value = item.hours_lecture;
                editHoursPractice.value = item.hours_practice;
                editHoursLab.value = item.hours_lab;
                editControlForm.value = item.control_form;
                
                modal.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Ошибка:', error);
        }
    };

    // Закрытие модалки
    document.getElementById('cancelEditBtn').addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    // Сохранение (создание или обновление)
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = editId.value;
        const payload = {
            name: editName.value,
            description: editDescription.value,
            hours_lecture: parseInt(editHoursLecture.value) || 0,
            hours_practice: parseInt(editHoursPractice.value) || 0,
            hours_lab: parseInt(editHoursLab.value) || 0,
            control_form: editControlForm.value
        };

        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_URL}${id}/` : API_URL;

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // На случай если csrf_exempt не сработает
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                modal.classList.add('hidden');
                loadDisciplines();
            } else {
                const err = await response.json();
                alert('Ошибка: ' + (err.error || 'Не удалось сохранить'));
            }
        } catch (error) {
            console.error('Ошибка:', error);
        }
    });

    // Удаление
    window.deleteDiscipline = async (id) => {
        if (!confirm('Вы уверены, что хотите удалить дисциплину?')) return;

        try {
            const response = await fetch(`${API_URL}${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            if (response.ok) {
                loadDisciplines();
            } else {
                alert('Ошибка при удалении');
            }
        } catch (error) {
            console.error('Ошибка:', error);
        }
    };

    // Слушатели фильтров
    filterSearch.addEventListener('input', loadDisciplines);
    filterControlForm.addEventListener('change', loadDisciplines);

    // Хелпер для CSRF-токена (если понадобится)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Первичная загрузка
    loadDisciplines();
});