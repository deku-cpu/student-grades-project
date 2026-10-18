// Ждем, пока страница полностью загрузится
document.addEventListener('DOMContentLoaded', function() {
    
    // Находим на странице элементы, с которыми будем работать
    const tableBody = document.getElementById('groups-body'); // Тело таблицы
    
    const modal = document.getElementById('editingModal');
    const form = document.getElementById('editFormTag');

    function loadGroups() {
        // Берем то, что ввели в фильтры
        let search = document.getElementById('filterName').value;
        let course = document.getElementById('filterYearOfStudy').value;
        let formVal = document.getElementById('filterEduForm').value;
        let specialization = document.getElementById("filterSpecialization").value;

        // Собираем ссылку для запроса
        let url = '/api/groups/?search=' + search + '&course=' + course + '&form=' + formVal + '&specialty=' + specialization;

        // Стучимся на сервер за данными
        fetch(url).then(function(response) {
            return response.json(); // Сервер отвечает, мы превращаем ответ в список
        }).then(function(groups) {
            window.allGroups = groups; 
            tableBody.innerHTML = ''; // Очищаем таблицу от старых данных

            // Если сервер вернул ошибку (например, студенту нельзя)
            if (!Array.isArray(groups)) {
                tableBody.innerHTML = '<tr><td colspan="8">Доступ ограничен</td></tr>';
                return; // Останавливаемся
            }

            // Пробегаемся по каждой группе по очереди
            for (let i = 0; i < groups.length; i++) {
                let g = groups[i]; // Берем одну группу
                
                // Создаем кнопки 
                let buttons = '<button onclick="journalGroup(' + g.id + ')" class="btn btn--secondary">Журнал</button> ' +
                              '<button onclick="editGroup(' + g.id + ')" class="btn btn--secondary">Ред.</button> ' +
                              '<button onclick="deleteGroup(' + g.id + ')" class="btn btn--secondary">Удалить</button>';

                // Лепим строчку для таблицы
                let row = '<tr>' +
                    '<td>' + g.id + '</td>' +
                    '<td>' + g.name + '</td>' +
                    '<td>' + g.yearOfStudy + '</td>' +
                    '<td>' + g.specialty + '</td>' +
                    '<td>' + g.form + '</td>' +
                    '<td>' + g.admissionYear + '</td>' +
                    '<td>' + g.students + '</td>' +
                    '<td>' + buttons + '</td>' +
                '</tr>';

                // Вставляем эту строчку в конец таблицы
                tableBody.innerHTML += row;
            }
        });
    }

    window.journalGroup = function(id){
        //группу из списка
        window.location.href = '/groups/' + id + '/journal/';
    }

    // (эта функция при "Ред.")
    window.editGroup = function(id) {
        
        // Находим группу по ID в загруженном списке
        let g = window.allGroups.find(x => x.id === id);
        
        if (g) {
            document.getElementById('editId').value = g.id;
            document.getElementById('editName').value = g.name;
            document.getElementById('editYearOfStudy').value = g.yearOfStudy;
            document.getElementById('editSpecialization').value = g.specialty_id; // ID специальности
            document.getElementById('editForm').value = g.form;
            document.getElementById('editAdmissionYear').value = g.admissionYear;
            
            document.getElementById('editStudentCount').value = g.students; 
            modal.classList.remove('hidden');
        }
    };

    // (вызывается из кнопки "Удалить")
    window.deleteGroup = function(id) {
        let ask = confirm('Точно удалить эту группу?'); // Спрашиваем пользователя
        if (ask === true) {
            // Отправляем запрос на удаление
            fetch('/api/groups/' + id + '/', { method: 'DELETE' })
            .then(function() {
                loadGroups(); // Обновляем таблицу после удаления
            });
        }
    };

    let addBtn = document.getElementById('addGroupBtn');
    if (addBtn) {
        addBtn.onclick = function() {
            form.reset(); // Очищаем все поля в окне
            document.getElementById('editId').value = ''; // Стираем ID (значит, создаем нового)
            modal.classList.remove('hidden'); // Открываем окно
        };
    }

   
    form.onsubmit = function(event) {
        event.preventDefault(); // Не даем странице перезагрузиться

        let id = document.getElementById('editId').value; // Берем ID (пустой или с цифрой)
        
        // Собираем данные из полей
        let data = {
            name: document.getElementById('editName').value,
            course: document.getElementById('editYearOfStudy').value,
            specialty: document.getElementById('editSpecialization').value,
            form: document.getElementById('editForm').value,
            admissionYear: document.getElementById('editAdmissionYear').value
        };

        // Если ID пустой - создаем (POST), если есть - меняем (PUT)
        let url = '/api/groups/';
        let method = 'POST';
        
        if (id !== '') {
            url = '/api/groups/' + id + '/';
            method = 'PUT';
        }

        // Отправляем данные на сервер
        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data) // Превращаем данные в текст для сервера
        }).then(function(response) {
            if (response.ok) {
                modal.classList.add('hidden'); // Закрываем окно
                loadGroups(); // Обновляем таблицу
            } else {
                alert('Ошибка сохранения!');
            }
        });
    };


    document.getElementById('cancelEditBtn').onclick = function() {
        modal.classList.add('hidden'); // Просто прячем окно
    };


    document.getElementById('filterName').oninput = loadGroups;
    document.getElementById('filterYearOfStudy').onchange = loadGroups;
    document.getElementById('filterEduForm').onchange = loadGroups;
    document.getElementById('filterSpecialization').onchange = loadGroups;

    // Запускаем загрузку при открытии страницы
    loadGroups();
});