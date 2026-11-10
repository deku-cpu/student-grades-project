document.addEventListener('DOMContentLoaded', async function() {
    const body = document.getElementById('diary-body');
    try {
        const data = await getJson('/api/student/diary/');
        if (!data.length) { body.innerHTML = '<tr><td colspan="4">Учебный план пока не назначен</td></tr>'; return; }
        body.innerHTML = '';
        data.forEach(function(item) {
            const grades = item.assignments.filter(a => item.grades[a.id]).map(a => escapeHtml(a.title) + ': <b>' + escapeHtml(formatGrade(item.grades[a.id])) + '</b>').join('<br>') || 'Оценок нет';
            body.innerHTML += '<tr><td>' + escapeHtml(item.discipline) + '<br><small>' + escapeHtml(item.semester + ', ' + item.group) + '</small></td><td>' + escapeHtml(item.teacher) + '</td><td>' + grades + '</td><td><b>' + escapeHtml(formatGrade(item.final_grade)) + '</b></td></tr>';
        });
    } catch (error) { body.innerHTML = '<tr><td colspan="4">' + escapeHtml(error.message) + '</td></tr>'; }
});
