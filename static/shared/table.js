/**
 * Универсальный рендер таблицы.
 * Ничего не знает про предметную область.
 *
 * @param {HTMLElement} container
 * @param {Object} config
 * @param {Array}  config.columns   - [{ key, label, render? }]
 * @param {Array}  config.rows      - данные
 * @param {Array}  [config.actions] - [{ label, className?, onClick(row) }]
 * @param {string} [config.emptyText]
 */
function createTable(container, config) {
    const { columns = [], actions = [], emptyText = 'Нет данных' } = config;
    let rows = config.rows || [];

    //рендер шапки
    function renderHead() {
        const ths = columns.map(c => `<th>${c.label}</th>`).join('');
        const actionTh = actions.length ? '<th>Действия</th>' : '';
        return `<thead><tr>${ths}${actionTh}</tr></thead>`;
    }

    //рендер одной строки
    function renderRow(row) {
        const cells = columns.map(c => {
            const value = c.render ? c.render(row) : row[c.key];
            return `<td>${value ?? ''}</td>`;
        }).join('');

        const actionCells = actions.length
            ? `<td>${actions.map((a, i) => `
                <button class="btn ${a.className || 'btn--secondary'}"
                        data-action="${i}"
                        data-id="${row.id}">
                    ${a.label}
                </button>
              `).join(' ')}</td>`
            : '';

        return `<tr>${cells}${actionCells}</tr>`;
    }

    function render() {
        if (!rows.length) {
            container.innerHTML = `<div class="empty">${emptyText}</div>`;
            return;
        }
        const body = rows.map(renderRow).join('');
        container.innerHTML = `<table>${renderHead()}<tbody>${body}</tbody></table>`;
    }

    //один обработчик на все кнопки
    container.addEventListener('click', (event) => {
        const btn = event.target.closest('button[data-action]');
        if (!btn) return;

        const action = actions[Number(btn.dataset.action)];
        const row = rows.find(r => String(r.id) === btn.dataset.id);
        if (action && row) action.onClick?.(row);
    });

    //публичное API
    render();

    return {
        render,
        update(newRows) {
            rows = newRows;
            render();
        },
        getRows() {
            return rows;
        }
    };
}