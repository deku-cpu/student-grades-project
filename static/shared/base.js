function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, function(char) {
        return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char];
    });
}

function formatGrade(value) {
    return value === 'pass' ? 'Зачёт' : value === 'fail' ? 'Незачёт' : value ?? '—';
}

// Общий fetch добавляет CSRF только к запросам нашего сайта.
const originalFetch = window.fetch.bind(window);
window.fetch = function(resource, options) {
    const request = resource instanceof Request ? resource : null;
    const url = new URL(request ? request.url : resource, window.location.href);
    options = Object.assign({}, options || {});
    const method = (options.method || (request && request.method) || 'GET').toUpperCase();
    if (url.origin === window.location.origin && !['GET', 'HEAD', 'OPTIONS'].includes(method)) {
        const token = document.cookie.split('; ').find(function(cookie) { return cookie.startsWith('csrftoken='); });
        const headers = new Headers(options.headers || (request && request.headers) || {});
        if (token) headers.set('X-CSRFToken', decodeURIComponent(token.slice('csrftoken='.length)));
        options.headers = headers;
    }
    return originalFetch(resource, options);
};

async function getJson(url, options) {
    const res = await fetch(url, options);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Не удалось выполнить запрос');
    return data;
}

function showError(error) {
    alert(error.message || 'Ошибка соединения с сервером');
}

document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function() {
            try {
                await getJson('/api/logout/', {method: 'POST'});
                localStorage.removeItem('role');
                window.location.href = '/login/';
            } catch (error) { showError(error); }
        });
    }

    // Сортировка работает и у таблиц, которые заполняются после загрузки страницы.
    document.addEventListener('click', function(event) {
        const header = event.target.closest('thead th');
        if (!header || event.target.closest('button, input, select') || header.textContent.trim() === 'Действия') return;
        const table = header.closest('table');
        const body = table.tBodies[0];
        if (!body) return;
        const column = header.cellIndex;
        const direction = header.dataset.direction === 'asc' ? -1 : 1;
        const rows = Array.from(body.rows);
        if (rows.some(row => row.cells.length !== table.tHead.rows[0].cells.length)) return;
        rows.sort(function(a, b) {
            const cellValue = function(row) {
                const input = row.cells[column].querySelector('input, select');
                return input ? input.value : row.cells[column].textContent.trim();
            };
            const left = cellValue(a), right = cellValue(b);
            return direction * left.localeCompare(right, 'ru', {numeric: true, sensitivity: 'base'});
        });
        rows.forEach(row => body.appendChild(row));
        header.dataset.direction = direction === 1 ? 'asc' : 'desc';
    });
});
