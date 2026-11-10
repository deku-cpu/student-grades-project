function showReportError(error) {
    const report = document.getElementById('report');
    if (report) report.textContent = error.message || 'Не удалось загрузить отчёт';
    const print = document.getElementById('printBtn');
    if (print) print.disabled = true;
}

async function reportTask(task) {
    try { await task(); } catch (error) { showReportError(error); }
}

document.addEventListener('DOMContentLoaded', function() {
    const match = window.location.pathname.match(/^\/reports\/([^/]+)\/$/);
    if (!match) return;
    const print = document.getElementById('printBtn');
    if (!print) return;
    const button = document.createElement('button');
    button.className = 'btn btn--secondary';
    button.textContent = 'Скачать Excel';
    button.type = 'button';
    print.after(button);
    button.onclick = function() {
        const params = new URLSearchParams({format: 'xlsx'});
        const teaching = document.getElementById('teachingSelect');
        const student = document.getElementById('studentSelect');
        const group = document.getElementById('groupSelect');
        const by = document.getElementById('bySelect');
        if (teaching || student || match[1] === 'group-rating') {
            const select = teaching || student || group;
            if (!select.value) { alert('Сначала выберите данные для отчёта'); return; }
        }
        if (teaching && teaching.value) params.set('teaching_id', teaching.value);
        if (student && student.value) params.set('student_id', student.value);
        if (group && group.value) params.set('group_id', group.value);
        if (by) params.set('by', by.value);
        window.location.href = '/api/reports/' + match[1] + '/?' + params;
    };
});
