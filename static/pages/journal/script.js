document.addEventListener('DOMContentLoaded', async function() {
    const title = document.getElementById('journal-title');
    const head = document.getElementById('journal-head');
    const body = document.getElementById('journal-body');
    const teachingId = document.getElementById('config').dataset.teachingId;
    try {
        const data = await getJson('/api/journal/' + teachingId + '/');
        title.textContent = 'Журнал: ' + data.group_name + ' — ' + data.discipline_name;
        head.innerHTML = '<tr><th>Студент</th>' + data.assignments.map(a => '<th>' + escapeHtml(a.title) + '<br><small>вес ' + escapeHtml(a.weight) + '</small></th>').join('') + '<th>Итог</th></tr>';
        body.innerHTML = '';
        data.students.forEach(function(student) {
            const row = document.createElement('tr');
            row.innerHTML = '<td>' + escapeHtml(student.full_name) + (student.transferred ? ' (переведён)' : '') + '</td>';
            data.assignments.forEach(function(assignment) {
                const cell = document.createElement('td');
                const input = document.createElement('select');
                input.className = 'grade-input';
                const isCredit = data.control_form === 'credit' && assignment.grade_type === 'final';
                const values = isCredit ? ['', 'pass', 'fail'] : data.control_form === 'credit' ? ['', '2', '3', '4', '5', 'pass', 'fail'] : ['', '2', '3', '4', '5'];
                values.forEach(function(value) {
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = value ? formatGrade(value) : '—';
                    input.appendChild(option);
                });
                input.value = student.grades[assignment.id] || '';
                let savedValue = input.value;
                input.addEventListener('change', async function() {
                    if (savedValue && !confirm('Изменить оценку?')) { input.value = savedValue; return; }
                    input.disabled = true;
                    try {
                        const result = await getJson('/api/journal/grade/', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({student_id: student.id, assignment_id: assignment.id, value: input.value})});
                        savedValue = input.value;
                        const final = row.querySelector('.final-grade');
                        final.textContent = formatGrade(result.final_grade);
                        final.title = result.weighted_average == null ? '' : 'Взвешенный балл: ' + result.weighted_average;
                    } catch (error) { input.value = savedValue; showError(error); }
                    finally { input.disabled = false; }
                });
                cell.appendChild(input);
                row.appendChild(cell);
            });
            const finalCell = document.createElement('td');
            const final = document.createElement('b');
            final.className = 'final-grade';
            final.textContent = formatGrade(student.final_grade);
            final.title = student.weighted_average == null ? '' : 'Взвешенный балл: ' + student.weighted_average;
            finalCell.appendChild(final);
            row.appendChild(finalCell);
            body.appendChild(row);
        });
        if (!data.students.length) body.innerHTML = '<tr><td colspan="' + (data.assignments.length + 2) + '">В группе пока нет студентов</td></tr>';
    } catch (error) { title.textContent = error.message; }
});
