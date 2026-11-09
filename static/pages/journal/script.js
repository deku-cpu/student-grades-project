document.addEventListener('DOMContentLoaded', function() {
    const titleElement = document.getElementById('journal-title');
    const thead = document.getElementById('journal-head');
    const tbody = document.getElementById('journal-body');
    const teachingId = document.getElementById('config').dataset.teachingId;

    fetch('/api/journal/' + teachingId + '/')
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.error) {
            titleElement.textContent = 'Ошибка: ' + data.error;
            return;
        }

        titleElement.textContent = 'Журнал: ' + data.group_name + ' — ' + data.discipline_name;

        // Рисуем шапку
        let headRow = '<tr><th>Студент</th>';
        for (let i = 0; i < data.assignments.length; i++) {
            headRow += '<th>' + data.assignments[i].title + '</th>';
        }
        headRow += '<th>Итог</th></tr>';
        thead.innerHTML = headRow;

        tbody.innerHTML = '';

        // Рисуем студентов
        for (let i = 0; i < data.students.length; i++) {
            let student = data.students[i];
            let row = '<tr><td>' + student.full_name + '</td>';

            for (let j = 0; j < data.assignments.length; j++) {
                let assignment = data.assignments[j];
                let gradeValue = student.grades[assignment.id] || '';
                
                row += '<td>' +
                    '<input type="text" class="grade-input" ' +
                    'value="' + gradeValue + '" ' +
                    'data-student="' + student.id + '" ' +
                    'data-assignment="' + assignment.id + '" ' +
                    'data-weight="' + assignment.weight + '" ' +
                    'style="width: 50px; padding: 4px; text-align: center;">' +
                '</td>';
            }

            row += '<td><b class="final-grade">—</b></td></tr>';
            tbody.innerHTML += row;
        }

        // расчет итоговых
        let allRows = tbody.querySelectorAll('tr');
        allRows.forEach(function(row) {
            updateRowTotal(row);
        });
        
        const inputs = document.querySelectorAll('.grade-input');
        
        inputs.forEach(function(input) {
            // Когда препод меняет оценку и нажимает Enter или кликает 
            input.addEventListener('change', function() {

                let row = this.closest('tr'); 
                updateRowTotal(row);


                let studentId = this.dataset.student;
                let assignmentId = this.dataset.assignment;
                let value = this.value;

                // Отправляем на сервер
                fetch('/api/journal/grade/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        student_id: studentId,
                        assignment_id: assignmentId,
                        value: value
                    })
                }).then(function(response) {
                    return response.json();
                }).then(function(res) {
                    if (res.error) {
                        alert(res.error);
                    } else {
                        console.log('Оценка сохранена!');
                    }
                });
            });
        });
    })
    .catch(function(error) {
        titleElement.textContent = 'Ошибка загрузки';
        console.error(error);
    });
});

function updateRowTotal(row) {
    let inputs = row.querySelectorAll('.grade-input');
    let totalScore = 0;
    let totalWeight = 0;
    
    inputs.forEach(function(input) {
        let gradeValue = input.value;
        let weight = parseFloat(input.dataset.weight);
        
        if (gradeValue && !isNaN(gradeValue)) {
            totalScore += parseFloat(gradeValue) * weight;
            totalWeight += weight;
        }
    });

    let finalGradeElement = row.querySelector('.final-grade');
    let finalGrade = '—';
    if (totalWeight > 0) {
        finalGrade = (totalScore / totalWeight).toFixed(2);
    }
    finalGradeElement.textContent = finalGrade;
}
