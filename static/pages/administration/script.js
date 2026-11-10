document.addEventListener('DOMContentLoaded', function() {
    const body = document.getElementById('audit-body');
    async function load() {
        try {
            const logs = await getJson('/api/admin/audit/?search=' + encodeURIComponent(document.getElementById('filterSearch').value));
            body.innerHTML = logs.map(log => '<tr><td>' + escapeHtml(log.created_at) + '</td><td>' + escapeHtml(log.user) + '</td><td>' + escapeHtml(log.action) + '</td><td>' + escapeHtml(log.path) + '</td></tr>').join('') || '<tr><td colspan="4">Действий пока нет</td></tr>';
        } catch (error) { body.innerHTML = '<tr><td colspan="4">' + escapeHtml(error.message) + '</td></tr>'; }
    }
    document.getElementById('filterSearch').oninput = load;
    document.getElementById('backupBtn').onclick = async function() {
        const button = this;
        button.disabled = true;
        try {
            const res = await fetch('/api/admin/backup/', {method: 'POST'});
            if (!res.ok) throw new Error((await res.json()).error);
            const url = URL.createObjectURL(await res.blob());
            const link = document.createElement('a');
            link.href = url;
            link.download = (res.headers.get('Content-Disposition').match(/filename="([^"]+)"/) || [null, 'backup.json'])[1];
            document.body.appendChild(link);
            link.click();
            link.remove();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
            await load();
        } catch (error) { showError(error); }
        finally { button.disabled = false; }
    };
    load();
});
