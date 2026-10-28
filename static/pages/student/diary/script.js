document.addEventListener('DOMContentLoaded', function() {
    const tbody = document.getElementById('diary-body');

    fetch('/api/student/diary/')
    .then(response => response.json())
    .then(data => {
        if (!Array.isArray(data)) {
            tbody.innerHTML = '<tr><td colspan="4">' + data.error + '</td></tr>';
            return;
        }

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">У вас пока нет оценок</td></tr>';
            return;
        }

        tbody.innerHTML = '';

        for (let i = 0; i < data.length; i++) {
            let item = data[i];
            
            // Собираем оценки в строку (например: "Лабораторная №1: 5, Контрольная: 4")
            let gradesText = '';
            let hasGrades = false;
            
            item.assignments.forEach(a => {
                let val = item.grades[a.id];
                if (val) {
                    gradesText += a.title + ': <b>' + val + '</b><br>';
                    hasGrades = true;
                }
            });

            if (!hasGrades) {
                gradesText = 'Оценок нет';
            }

            let row = '<tr>' +
                '<td>' + item.discipline + '</td>' +
                '<td>' + item.teacher + '</td>' +
                '<td>' + gradesText + '</td>' +
                '<td><b>' + item.final_grade + '</b></td>' +
            '</tr>';
            
            tbody.innerHTML += row;
        }
    })
    .catch(error => {
        tbody.innerHTML = '<tr><td colspan="4">Ошибка загрузки данных</td></tr>';
        console.error(error);
    });
});