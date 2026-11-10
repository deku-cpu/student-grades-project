document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.getElementById('teachings-body');
    const modal = document.getElementById('editingModal');
    const form = document.getElementById('editFormTag');

    function loadTeachings() {
        let search = document.getElementById('filterSearch').value;
        let url = '/api/teachings/?search=' + encodeURIComponent(search);

        fetch(url)
        .then(response => response.json())
        .then(teachings => {
            window.allTeachings = teachings; 
            tableBody.innerHTML = '';

            if (!Array.isArray(teachings)) {
                tableBody.innerHTML = '<tr><td colspan="6">Доступ ограничен</td></tr>';
                return;
            }

            for (let i = 0; i < teachings.length; i++) {
                let t = teachings[i];
                
                // Кнопки: Задания, Ред., Удалить
                let buttons = '<button onclick="goToAssignments(' + t.id + ')" class="btn btn--secondary">Задания</button> ' +
                              '<a class="btn btn--secondary" href="/journal/' + t.id + '/">Журнал</a> ' +
                              '<button onclick="editTeaching(' + t.id + ')" class="btn btn--secondary">Ред.</button> ' +
                              '<button onclick="deleteTeaching(' + t.id + ')" class="btn btn--secondary">Удалить</button>';

                let row = '<tr>' +
                    '<td>' + escapeHtml(t.id) + '</td>' +
                    '<td>' + escapeHtml(t.group_name) + '</td>' +
                    '<td>' + escapeHtml(t.discipline_name) + '</td>' +
                    '<td>' + escapeHtml(t.teacher_name) + '</td>' +
                    '<td>' + escapeHtml(t.semester_name) + '</td>' +
                    '<td>' + buttons + '</td>' +
                '</tr>';
                tableBody.innerHTML += row;
            }
        });
    }

    // Переход на страницу заданий
    window.goToAssignments = function(id) {
        window.location.href = '/teachings/' + id + '/assignments/';
    }

    window.editTeaching = function(id) {
        let t = window.allTeachings.find(x => x.id === id);
        if (t) {
            document.getElementById('editId').value = t.id;
            document.getElementById('editGroup').value = t.group_id;
            document.getElementById('editDiscipline').value = t.discipline_id;
            document.getElementById('editTeacher').value = t.teacher_id;
            document.getElementById('editSemester').value = t.semester_id;
            
            modal.classList.remove('hidden');
        }
    };

    window.deleteTeaching = function(id) {
        if (confirm('Точно удалить эту пару?')) {
            fetch('/api/teachings/' + id + '/', { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    loadTeachings();
                } else {
                    return response.json().then(err => alert('Ошибка: ' + err.error));
                }
            });
        }
    };

    document.getElementById('addTeachingBtn').onclick = function() {
        form.reset();
        document.getElementById('editId').value = '';
        modal.classList.remove('hidden');
    };

    form.onsubmit = function(event) {
        event.preventDefault();
        let id = document.getElementById('editId').value;
        if (id && !confirm('Сохранить изменения?')) return;
        
        let data = {
            group_id: document.getElementById('editGroup').value,
            discipline_id: document.getElementById('editDiscipline').value,
            teacher_id: document.getElementById('editTeacher').value,
            semester_id: document.getElementById('editSemester').value
        };

        let url = '/api/teachings/';
        let method = 'POST';
        
        if (id !== '') {
            url = '/api/teachings/' + id + '/';
            method = 'PUT';
        }

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(response => {
            if (response.ok) {
                modal.classList.add('hidden');
                loadTeachings();
            } else {
                return response.json().then(err => alert('Ошибка сохранения: ' + err.error));
            }
        });
    };

    document.getElementById('cancelEditBtn').onclick = () => modal.classList.add('hidden');
    document.getElementById('filterSearch').oninput = loadTeachings;

    loadTeachings();
});
