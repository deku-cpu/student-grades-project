document.addEventListener('DOMContentLoaded', function() {
    const config = JSON.parse(document.getElementById('reference-config').textContent);
    const body = document.getElementById('records-body');
    const form = document.getElementById('editFormTag');
    const modal = document.getElementById('editingModal');
    let records = [];

    async function load() {
        try {
            records = await getJson(config.url + '?search=' + encodeURIComponent(document.getElementById('filterSearch').value));
            body.innerHTML = '';
            records.forEach(function(record) {
                const row = document.createElement('tr');
                row.innerHTML = '<td>' + record.id + '</td>' + config.fields.map(field => '<td>' + escapeHtml(record[field.name]) + '</td>').join('') + '<td><button class="btn btn--secondary" data-edit="' + record.id + '">Ред.</button> <button class="btn btn--secondary" data-delete="' + record.id + '">Удалить</button></td>';
                body.appendChild(row);
            });
            if (!records.length) body.innerHTML = '<tr><td colspan="' + (config.fields.length + 2) + '">Записей нет</td></tr>';
        } catch (error) { body.innerHTML = '<tr><td>' + escapeHtml(error.message) + '</td></tr>'; }
    }

    document.getElementById('addRecordBtn').onclick = function() { form.reset(); document.getElementById('editId').value = ''; modal.classList.remove('hidden'); };
    document.getElementById('cancelEditBtn').onclick = function() { modal.classList.add('hidden'); };
    document.getElementById('filterSearch').oninput = load;
    body.onclick = async function(event) {
        const edit = event.target.closest('[data-edit]');
        const remove = event.target.closest('[data-delete]');
        if (edit) {
            const record = records.find(item => item.id === Number(edit.dataset.edit));
            document.getElementById('editId').value = record.id;
            config.fields.forEach(field => { form.elements[field.name].value = record[field.name]; });
            modal.classList.remove('hidden');
        }
        if (remove && confirm('Точно удалить эту запись?')) {
            try { await getJson(config.url + remove.dataset.delete + '/', {method: 'DELETE'}); await load(); }
            catch (error) { showError(error); }
        }
    };
    form.onsubmit = async function(event) {
        event.preventDefault();
        const id = document.getElementById('editId').value;
        if (id && !confirm('Сохранить изменения?')) return;
        const data = {};
        config.fields.forEach(field => { data[field.name] = form.elements[field.name].value; });
        try {
            await getJson(config.url + (id ? id + '/' : ''), {method: id ? 'PUT' : 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
            modal.classList.add('hidden');
            await load();
        } catch (error) { showError(error); }
    };
    load();
});
