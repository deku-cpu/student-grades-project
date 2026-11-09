const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
    c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const sel = document.getElementById('groupSelect');
const report = document.getElementById('report');
const printBtn = document.getElementById('printBtn');

printBtn.addEventListener('click', () => window.print());

async function load() {
    report.innerHTML = '<p>Загрузка…</p>';
    const url = '/api/reports/debtors/' + (sel.value ? '?group_id=' + sel.value : '');
    const res = await fetch(url, { credentials: 'same-origin' });
    const d = await res.json();

    if (!d.length) {
        report.innerHTML = '<p>Должников нет.</p>';
        printBtn.disabled = true;
        return;
    }

    let html = `<h2>Должники (${d.length})</h2>
        <table><thead><tr>
            <th>Студент</th><th>Группа</th><th>Дисциплина</th><th>Семестр</th><th>Итог</th>
        </tr></thead><tbody>`;
    d.forEach(r => {
        html += `<tr>
            <td>${esc(r.student)}</td>
            <td>${esc(r.group)}</td>
            <td>${esc(r.discipline)}</td>
            <td>${esc(r.semester)}</td>
            <td class="final-grade">${r.final_grade}</td>
        </tr>`;
    });
    report.innerHTML = html + `</tbody></table>`;
    printBtn.disabled = false;
}

(async function init() {
    const res = await fetch('/api/groups/', { credentials: 'same-origin' });
    const data = await res.json();
    data.sort((a, b) => a.name.localeCompare(b.name));
    for (const g of data) {
        const o = document.createElement('option');
        o.value = g.id;
        o.textContent = g.name;
        sel.appendChild(o);
    }
    load();
})();

sel.addEventListener('change', load);