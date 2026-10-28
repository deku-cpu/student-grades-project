const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
    c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const sel = document.getElementById('groupSelect');
const report = document.getElementById('report');
const printBtn = document.getElementById('printBtn');

printBtn.addEventListener('click', () => window.print());

(async function loadGroups() {
    const res = await fetch('/api/groups/', { credentials: 'same-origin' });
    const data = await res.json();
    data.sort((a, b) => a.name.localeCompare(b.name));
    for (const g of data) {
        const o = document.createElement('option');
        o.value = g.id;
        o.textContent = g.name;
        sel.appendChild(o);
    }
})();

sel.addEventListener('change', async () => {
    if (!sel.value) { report.innerHTML = ''; printBtn.disabled = true; return; }
    report.innerHTML = '<p>Загрузка…</p>';
    const res = await fetch('/api/reports/group-rating/?group_id=' + sel.value,
                            { credentials: 'same-origin' });
    const d = await res.json();

    let html = `<h2>Рейтинг группы ${esc(d.group_name)}</h2>
        <table><thead><tr>
            <th>Место</th><th>Студент</th><th>Средний балл</th><th>Долгов</th>
        </tr></thead><tbody>`;

    d.students.forEach(s => {
        const cls = s.place <= 3 ? `place-${s.place}` : '';
        html += `<tr>
            <td class="${cls}">${s.place}</td>
            <td>${esc(s.full_name)}</td>
            <td><b>${s.avg_grade ?? '—'}</b></td>
            <td>${s.bad_count}</td>
        </tr>`;
    });

    report.innerHTML = html + `</tbody></table>`;
    printBtn.disabled = false;
});