const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
    c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const sel = document.getElementById('groupSelect');
const report = document.getElementById('report');
const printBtn = document.getElementById('printBtn');

printBtn.addEventListener('click', () => window.print());

async function load() {
    report.innerHTML = '<p>Загрузка…</p>';
    const url = '/api/reports/quality/' + (sel.value ? '?group_id=' + sel.value : '');
    const data = await getJson(url, { credentials: 'same-origin' });

    let html = `<h2>Качество знаний по группам</h2>
        <table><thead><tr>
            <th>Группа</th><th>Студентов</th><th>С оценками 4 и 5</th><th>Качество, %</th>
        </tr></thead><tbody>`;
    data.forEach(r => {
        html += `<tr>
            <td>${esc(r.group)}</td>
            <td>${r.students}</td>
            <td>${r.good}</td>
            <td><b>${r.quality_percent}%</b></td>
        </tr>`;
    });
    report.innerHTML = html + `</tbody></table>`;
}

(async function init() {
    const data = await getJson('/api/groups/', { credentials: 'same-origin' });
    data.sort((a, b) => a.name.localeCompare(b.name));
    for (const g of data) {
        const o = document.createElement('option');
        o.value = g.id;
        o.textContent = g.name;
        sel.appendChild(o);
    }
    await load();
})().catch(showReportError);

sel.addEventListener('change', () => reportTask(load));
