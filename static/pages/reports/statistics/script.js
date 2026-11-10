const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
    c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const sel = document.getElementById('bySelect');
const report = document.getElementById('report');
const printBtn = document.getElementById('printBtn');
const TITLES = { group: 'Группа', course: 'Курс', specialty: 'Специальность' };
const REPORT_TITLES = {group: 'Статистика по группам', course: 'Статистика по курсам', specialty: 'Статистика по специальностям'};

printBtn.addEventListener('click', () => window.print());

async function load() {
    report.innerHTML = '<p>Загрузка…</p>';
    const data = await getJson('/api/reports/statistics/?by=' + sel.value,
                            { credentials: 'same-origin' });

    let html = `<h2>${REPORT_TITLES[sel.value]}</h2>
        <table><thead><tr>
            <th>${TITLES[sel.value]}</th><th>Студентов</th>
            <th>Средний балл</th><th>Долгов</th>
        </tr></thead><tbody>`;
    data.forEach(r => {
        html += `<tr>
            <td>${esc(r.name)}</td>
            <td>${r.students}</td>
            <td><b>${r.avg_grade ?? '—'}</b></td>
            <td>${r.bad_count}</td>
        </tr>`;
    });
    report.innerHTML = html + `</tbody></table>`;
}

sel.addEventListener('change', () => reportTask(load));
reportTask(load);
