document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.getElementById('teachers-body');
    const modal = document.getElementById('editingModal');
    const form = document.getElementById('editFormTag');

    function loadTeachers() {
        let search = document.getElementById('filterName').value;
        let dept = document.getElementById('filterDepartment').value;
        let position = document.getElementById('filterPosition').value;

        let url = '/api/teachers/?search=' + search + '&department=' + dept + '&position=' + position;

        fetch(url)
        .then(response => response.json())
        .then(teachers => {
            window.allTeachers = teachers; 
            tableBody.innerHTML = '';

            if (!Array.isArray(teachers)) {
                tableBody.innerHTML = '<tr><td colspan="5">Доступ ограничен</td></tr>';
                return;
            }

            for (let i = 0; i < teachers.length; i++) {
                let t = teachers[i];
                
                let buttons = '<button onclick="editTeacher(' + t.id + ')" class="btn btn--secondary">Ред.</button> ' +
                              '<button onclick="deleteTeacher(' + t.id + ')" class="btn btn--secondary">Удалить</button>';

                let row = '<tr>' +
                    '<td>' + t.id + '</td>' +
                    '<td>' + t.full_name + '</td>' +
                    '<td>' + t.department_name + '</td>' +
                    '<td>' + t.position + '</td>' +
                    '<td>' + buttons + '</td>' +
                '</tr>';
                tableBody.innerHTML += row;
            }
        });
    }

    window.editTeacher = function(id) {
        let t = window.allTeachers.find(x => x.id === id);
        if (t) {
            document.getElementById('editId').value = t.id;
            document.getElementById('editLastName').value = t.last_name;
            document.getElementById('editFirstName').value = t.first_name;
            document.getElementById('editMiddleName').value = t.middle_name;
            document.getElementById('editDepartment').value = t.department_id;
            document.getElementById('editPosition').value = t.position;
            document.getElementById('editDegree').value = t.academic_degree;
            document.getElementById('editEmail').value = t.email;
            document.getElementById('editPhone').value = t.phone_number;
            
            modal.classList.remove('hidden');
        }
    };

    window.deleteTeacher = function(id) {
        if (confirm('Точно удалить преподавателя?')) {
            fetch('/api/teachers/' + id + '/', { method: 'DELETE' })
            .then(() => loadTeachers());
        }
    };

    document.getElementById('addTeacherBtn').onclick = function() {
        form.reset();
        document.getElementById('editId').value = '';
        modal.classList.remove('hidden');
    };

    form.onsubmit = function(event) {
        event.preventDefault();
        let id = document.getElementById('editId').value;
        
        let data = {
            last_name: document.getElementById('editLastName').value,
            first_name: document.getElementById('editFirstName').value,
            middle_name: document.getElementById('editMiddleName').value,
            department_id: document.getElementById('editDepartment').value,
            position: document.getElementById('editPosition').value,
            academic_degree: document.getElementById('editDegree').value,
            email: document.getElementById('editEmail').value,
            phone_number: document.getElementById('editPhone').value
        };

        let url = '/api/teachers/';
        let method = 'POST';
        
        if (id !== '') {
            url = '/api/teachers/' + id + '/';
            method = 'PUT';
        }

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(response => {
            if (response.ok) {
                modal.classList.add('hidden');
                loadTeachers();
            } else {
                alert('Ошибка сохранения! Проверьте поля.');
            }
        });
    };

    document.getElementById('cancelEditBtn').onclick = () => modal.classList.add('hidden');

    document.getElementById('filterName').oninput = loadTeachers;
    document.getElementById('filterDepartment').onchange = loadTeachers;
    document.getElementById('filterPosition').onchange = loadTeachers;

    loadTeachers();
});