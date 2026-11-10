document.addEventListener('DOMContentLoaded', async function() {
    const target = document.getElementById('rating');
    try {
        const data = await getJson('/api/student/rating/');
        target.innerHTML = '<table><tbody>' + [
            ['Студент', data.full_name], ['Группа', data.group_name],
            ['Средний балл', data.avg_grade ?? 'Нет оценок'],
            ['Место в группе', data.place == null ? 'Рейтинг ещё не рассчитан' : data.place + ' из ' + data.students_count],
            ['Дисциплин с долгом', data.bad_count]
        ].map(row => '<tr><th>' + row[0] + '</th><td>' + escapeHtml(row[1]) + '</td></tr>').join('') + '</tbody></table>';
    } catch (error) { target.textContent = error.message; }
});
