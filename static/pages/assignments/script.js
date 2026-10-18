document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.getElementById('assignments-body');
    const modal = document.getElementById('editingModal');
    const form = document.getElementById('editFormTag');
    const titleElement = document.getElementById('page-title');
    
    // Получаем ID пары из HTML
    const teachingId = document.getElementById('config').dataset.teachingId;

    // 1. Загружаем задания
    function loadAssignments() {
        fetch('/api/teachings/' + teachingId + '/assignments/')
        .then(response => response.json())
        .then(assignments => {
            window.allAssignments = assignments; 
            tableBody.innerHTML = '';

            if (!Array.isArray(assignments)) {
                tableBody.innerHTML = '<tr><td colspan="7">Ошибка загрузки</td></tr>';
                return;
            }

            if (assignments.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="7">Заданий пока нет</td></tr>';
                return;
            }

            for (let i = 0; i < assignments.length; i++) {
                let a = assignments[i];
                
                let buttons = '<button onclick="editAssignment(' + a.id + ')" class="btn btn--secondary">Ред.</button> ' +
                              '<button onclick="deleteAssignment(' + a.id + ')" class="btn btn--secondary">Удалить</button>';

                let row = '<tr>' +
                    '<td>' + a.id + '</td>' +
                    '<td>' + a.title + '</td>' +
                    '<td>' + a.grade_type + '</td>' +
                    '<td>' + a.weight + '</td>' +
                    '<td>' + a.order + '</td>' +
                    '<td>' + (a.date || '—') + '</td>' +
                    '<td>' + buttons + '</td>' +
                '</tr>';
                tableBody.innerHTML += row;
            }
        });
    }

    // 2. Узнаем название группы и дисциплины для заголовка (делаем запрос к API пар)
    fetch('/api/teachings/')
    .then(res => res.json())
    .then(data => {
        if (Array.isArray(data)) {
            let current = data.find(x => x.id == teachingId);
            if (current) {
                titleElement.textContent = 'Задания: ' + current.group_name + ' — ' + current.discipline_name;
            }
        }
    });

    // 3. Обработчики кнопок
    window.editAssignment = function(id) {
        let a = window.allAssignments.find(x => x.id === id);
        if (a) {
            document.getElementById('editId').value = a.id;
            document.getElementById('editTitle').value = a.title;
            document.getElementById('editType').value = a.grade_type;
            document.getElementById('editWeight').value = a.weight;
            document.getElementById('editOrder').value = a.order;
            document.getElementById('editDate').value = a.date;
            
            modal.classList.remove('hidden');
        }
    };

    window.deleteAssignment = function(id) {
        if (confirm('Точно удалить это задание?')) {
            fetch('/api/assignments/' + id + '/', { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    loadAssignments();
                } else {
                    return response.json().then(err => alert('Ошибка: ' + err.error));
                }
            });
        }
    };

    document.getElementById('addAssignmentBtn').onclick = function() {
        form.reset();
        document.getElementById('editId').value = '';
        document.getElementById('editOrder').value = '0'; // По умолчанию
        modal.classList.remove('hidden');
    };

    // 4. Сохранение
    form.onsubmit = function(event) {
        event.preventDefault();
        let id = document.getElementById('editId').value;
        
        let data = {
            title: document.getElementById('editTitle').value,
            grade_type: document.getElementById('editType').value,
            weight: document.getElementById('editWeight').value,
            order: document.getElementById('editOrder').value,
            date: document.getElementById('editDate').value
        };

        let url = '/api/teachings/' + teachingId + '/assignments/';
        let method = 'POST';
        
        if (id !== '') {
            // Если это редактирование, URL меняется (мы передаем id задания в другой API)
            url = '/api/assignments/' + id + '/';
            method = 'PUT';
        }

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(response => {
            if (response.ok) {
                modal.classList.add('hidden');
                loadAssignments();
            } else {
                return response.json().then(err => alert('Ошибка сохранения: ' + err.error));
            }
        });
    };

    document.getElementById('cancelEditBtn').onclick = () => modal.classList.add('hidden');

    // Первичная загрузка
    loadAssignments();
});