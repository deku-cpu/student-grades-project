document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.getElementById('students-body');
    const modal = document.getElementById('editingModal');
    const form = document.getElementById('editFormTag');

    function loadStudents() {
        let search = document.getElementById('filterName').value;
        let group = document.getElementById('filterGroup').value;
        let formVal = document.getElementById('filterForm').value;
        let status = document.getElementById('filterStatus').value;

        let url = '/api/students/?' + new URLSearchParams({search: search, group: group, form: formVal, status: status});

        fetch(url)
        .then(response => response.json())
        .then(students => {
            window.allStudents = students; 
            tableBody.innerHTML = '';

            if (!Array.isArray(students)) {
                tableBody.innerHTML = '<tr><td colspan="6">Доступ ограничен</td></tr>';
                return;
            }

            for (let i = 0; i < students.length; i++) {
                let s = students[i];
                
                let buttons = '<button onclick="cardStudent(' + s.id + ')" class="btn btn--secondary">Карточка</button> ' +
                              '<button onclick="editStudent(' + s.id + ')" class="btn btn--secondary">Ред.</button> ' +
                              '<button onclick="deleteStudent(' + s.id + ')" class="btn btn--secondary">Удалить</button>';

                let row = '<tr>' +
                    '<td>' + escapeHtml(s.id) + '</td>' +
                    '<td>' + escapeHtml(s.full_name) + '</td>' +
                    '<td>' + escapeHtml(s.group_name) + '</td>' +
                    '<td>' + escapeHtml(s.education_form_label) + '</td>' +
                    '<td>' + escapeHtml(s.status_label) + '</td>' +
                    '<td>' + buttons + '</td>' +
                '</tr>';
                tableBody.innerHTML += row;
            }
        });
    }

    window.cardStudent = function(id) {
        window.location.href = '/students/' + id + '/card/';
    }

    window.editStudent = function(id) {
        let s = window.allStudents.find(x => x.id === id);
        if (s) {
            document.getElementById('editId').value = s.id;
            document.getElementById('editLastName').value = s.last_name;
            document.getElementById('editFirstName').value = s.first_name;
            document.getElementById('editMiddleName').value = s.middle_name;
            document.getElementById('editGroup').value = s.group_id;
            document.getElementById('editForm').value = s.education_form;
            document.getElementById('editStatus').value = s.status;
            document.getElementById('editEmail').value = s.email;
            document.getElementById('editPhone').value = s.phone_number;
            document.getElementById('editGender').value = s.gender;
            document.getElementById('editDob').value = s.date_of_birth;
            document.getElementById('editAdmission').value = s.admission_date;
            
            modal.classList.remove('hidden');
        }
    };

    window.deleteStudent = function(id) {
        if (confirm('Точно удалить студента?')) {
            getJson('/api/students/' + id + '/', { method: 'DELETE' })
            .then(() => loadStudents())
            .catch(showError);
        }
    };

    document.getElementById('addStudentBtn').onclick = function() {
        form.reset();
        document.getElementById('editId').value = '';
        modal.classList.remove('hidden');
    };

    form.onsubmit = function(event) {
        event.preventDefault();
        let id = document.getElementById('editId').value;
        if (id && !confirm('Сохранить изменения?')) return;
        
        let data = {
            last_name: document.getElementById('editLastName').value,
            first_name: document.getElementById('editFirstName').value,
            middle_name: document.getElementById('editMiddleName').value,
            group_id: document.getElementById('editGroup').value,
            education_form: document.getElementById('editForm').value,
            status: document.getElementById('editStatus').value,
            email: document.getElementById('editEmail').value,
            phone_number: document.getElementById('editPhone').value,
            gender: document.getElementById('editGender').value,
            date_of_birth: document.getElementById('editDob').value,
            admission_date: document.getElementById('editAdmission').value
        };

        let url = '/api/students/';
        let method = 'POST';
        
        if (id !== '') {
            url = '/api/students/' + id + '/';
            method = 'PUT';
        }

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(response => {
            if (response.ok) {
                modal.classList.add('hidden');
                loadStudents();
            } else {
                alert('Ошибка сохранения! Проверьте поля.');
            }
        });
    };

    document.getElementById('cancelEditBtn').onclick = () => modal.classList.add('hidden');

    document.getElementById('filterName').oninput = loadStudents;
    document.getElementById('filterGroup').onchange = loadStudents;
    document.getElementById('filterForm').onchange = loadStudents;
    document.getElementById('filterStatus').onchange = loadStudents;

    loadStudents();
});
