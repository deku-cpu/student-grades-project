const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
    c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const sel = document.getElementById('studentSelect');
const report = document.getElementById('report');
const printBtn = document.getElementById('printBtn');

printBtn.addEventListener('click', () => window.print());

(async function loadStudents() {
    const data = await getJson('/api/students/', { credentials: 'same-origin' });
    data.sort((a, b) => a.full_name.localeCompare(b.full_name));
    for (const s of data) {
        const o = document.createElement('option');
        o.value = s.id;
        o.textContent = `${s.full_name} (${s.group_name || 'без группы'})`;
        sel.appendChild(o);
    }
    const selected = new URLSearchParams(window.location.search).get('student_id');
    if (selected) { sel.value = selected; sel.dispatchEvent(new Event('change')); }
})().catch(showReportError);

sel.addEventListener('change', () => reportTask(async () => {
    if (!sel.value) { report.innerHTML = ''; printBtn.disabled = true; return; }
    report.innerHTML = '<p>Загрузка…</p>';
    const d = await getJson('/api/reports/student-summary/?student_id=' + sel.value,
                            { credentials: 'same-origin' });

    let html = `
        <div class="report-header">
            <h2>${esc(d.full_name)}</h2>
            <table class="report-meta">
                <tr><td>Группа:</td><td><b>${esc(d.group_name || '—')}</b></td></tr>
                <tr><td>Специальность:</td><td>${esc(d.specialty || '—')}</td></tr>
                <tr><td>Курс:</td><td>${d.course ?? '—'}</td></tr>
                <tr><td>Форма обучения:</td><td>${esc(d.education_form)}</td></tr>
                <tr><td>Статус:</td><td>${esc(d.status)}</td></tr>
            </table>
        </div>
        <div class="report-stats">
            <p><b>Средний балл:</b> ${d.avg_grade ?? '—'}</p>
            <p><b>Дисциплин с долгом:</b> ${d.bad_count}</p>
        </div>
        <table><thead><tr>
            <th>Дисциплина</th><th>Семестр</th><th>Преподаватель</th>
            <th>Форма контроля</th><th>Оценки</th><th>Итог</th>
        </tr></thead><tbody>`;

    d.results.forEach(r => {
        const grades = r.assignments
            .map(a => `${esc(a.title)}: ${esc(formatGrade(a.value))}`)
            .join('<br>');
        html += `<tr>
            <td>${esc(r.discipline)}<br><small>${esc(r.group)}</small></td>
            <td>${esc(r.semester)}</td>
            <td>${esc(r.teacher)}</td>
            <td>${esc(r.control_form)}</td>
            <td class="grades-cell">${grades}</td>
            <td class="final-grade">${esc(formatGrade(r.final_grade))}</td>
        </tr>`;
    });

    report.innerHTML = html + `</tbody></table>`;
    printBtn.disabled = false;
}));