const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
    c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const sel = document.getElementById('teachingSelect');
const report = document.getElementById('report');
const printBtn = document.getElementById('printBtn');

printBtn.addEventListener('click', () => window.print());

(async function loadTeachings() {
    const res = await fetch('/api/teachings/', { credentials: 'same-origin' });
    const data = await res.json();
    data.sort((a, b) => a.group_name.localeCompare(b.group_name));
    for (const t of data) {
        const o = document.createElement('option');
        o.value = t.id;
        o.textContent = `${t.group_name} — ${t.discipline_name} (${t.semester_name}, ${t.teacher_name})`;
        sel.appendChild(o);
    }
})();

sel.addEventListener('change', async () => {
    if (!sel.value) { report.innerHTML = ''; printBtn.disabled = true; return; }
    report.innerHTML = '<p>Загрузка…</p>';
    const res = await fetch('/api/reports/statement/?teaching_id=' + sel.value,
                            { credentials: 'same-origin' });
    const d = await res.json();

    let html = `
        <div class="report-header">
            <h2>Ведомость успеваемости</h2>
            <table class="report-meta">
                <tr><td>Группа:</td><td><b>${esc(d.group_name)}</b></td></tr>
                <tr><td>Дисциплина:</td><td><b>${esc(d.discipline_name)}</b></td></tr>
                <tr><td>Семестр:</td><td>${esc(d.semester)}</td></tr>
                <tr><td>Преподаватель:</td><td>${esc(d.teacher)}</td></tr>
            </table>
        </div>
        <table><thead><tr><th>№</th><th>Студент</th>`;

    d.assignments.forEach(a => {
        html += `<th>${esc(a.title)}<br><small>вес ${a.weight}</small></th>`;
    });
    html += `<th>Итог</th></tr></thead><tbody>`;

    d.students.forEach((s, i) => {
        html += `<tr><td>${i + 1}</td><td>${esc(s.full_name)}</td>`;
        d.assignments.forEach(a => html += `<td>${esc(s.grades[a.id] ?? '—')}</td>`);
        html += `<td class="final-grade">${s.final_grade ?? '—'}</td></tr>`;
    });
    html += `</tbody></table>
        <div class="report-stats">
            <p><b>Студентов:</b> ${d.students.length}</p>
            <p><b>Средний балл:</b> ${d.avg_grade ?? '—'}</p>
            <p><b>Качество знаний (4–5):</b> ${d.quality_percent}%</p>
            <p><b>Абсолютная успеваемость (3–5):</b> ${d.absolute_percent}%</p>
        </div>`;

    report.innerHTML = html;
    printBtn.disabled = false;
});