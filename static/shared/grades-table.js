/**
 * Матрица оценок: строки × занятия.
 *
 * @param {HTMLElement} container
 * @param {Object} config
 * @param {Array}  config.students  - [{ id, name }]  — строки (ученики / предметы)
 * @param {Array}  config.lessons   - [{ id, date, topic, type }]  — колонки
 * @param {Object} config.grades    - { [rowId]: { [lessonId]: value } }
 * @param {boolean} [config.editable] - true → input, false → текст
 * @param {boolean} [config.withAverage] - показывать колонку «Ср. балл»
 * @param {boolean} [config.withColumnActions] - показывать «+» и «×» в шапке
 * @param {string}  [config.firstColumnLabel] - заголовок первого столбца (по умолчанию «Ученик»)
 * @param {Function} [config.onChange]       - (rowId, lessonId, value) => {}
 * @param {Function} [config.onAddLesson]    - () => {}
 * @param {Function} [config.onRemoveLesson] - (lesson) => {}
 */
function createGradesTable(container, config) {
    const {
        students = [],
        lessons = [],
        grades = {},
        editable = false,
        withAverage = false,
        withColumnActions = false,
        firstColumnLabel = 'Ученик',
        onChange,
        onAddLesson,
        onRemoveLesson
    } = config;

    function cell(student, lesson) {
        const value = grades[student.id]?.[lesson.id] ?? '';

        if (!editable) {
            return `<td class="grades-cell">${value}</td>`;
        }

        return `<td>
            <input class="grades-input"
                   type="text"
                   maxlength="2"
                   value="${value}"
                   data-student="${student.id}"
                   data-lesson="${lesson.id}">
        </td>`;
    }

    // шапка
    function renderHead() {
        const lessonThs = lessons.map(l => `
            <th>
                <div>${l.date}</div>
                <div class="grades-th-topic">${l.topic}</div>
                ${withColumnActions
            ? `<button class="grades-col-remove"
                               data-remove-lesson="${l.id}"
                               title="Удалить колонку">×</button>`
            : ''}
            </th>
        `).join('');

        const addTh = withColumnActions
            ? `<th class="grades-th-add">
                   <button class="grades-col-add"
                           id="addLessonColBtn"
                           title="Добавить занятие">+</button>
               </th>`
            : '';

        const avgTh = withAverage
            ? `<th class="grades-sticky-avg">Ср. балл</th>`
            : '';

        return `
            <thead>
                <tr>
                    <th class="grades-sticky-col">${firstColumnLabel}</th>
                    ${lessonThs}
                    ${addTh}
                    ${avgTh}
                </tr>
            </thead>
        `;
    }

    //строки
    function renderRow(student) {
        const cells = lessons.map(l => cell(student, l)).join('');

        const addCell = withColumnActions ? `<td class="grades-cell-add"></td>` : '';

        const avgCell = withAverage
            ? `<td class="grades-sticky-avg" data-avg-student="${student.id}">—</td>`
            : '';

        return `
            <tr>
                <td class="grades-sticky-col">${student.name}</td>
                ${cells}
                ${addCell}
                ${avgCell}
            </tr>
        `;
    }

    function render() {
        if (!students.length || !lessons.length) {
            container.innerHTML = `<div class="empty">Нет данных для отображения</div>`;
            return;
        }

        const head = renderHead();
        const body = students.map(renderRow).join('');

        container.innerHTML = `
            <table class="grades-table">
                ${head}
                <tbody>${body}</tbody>
            </table>
        `;
    }

    //автосохранение
    if (editable) {
        container.addEventListener('change', (event) => {
            const input = event.target.closest('.grades-input');
            if (!input) return;

            const studentId = Number(input.dataset.student);
            const lessonId  = Number(input.dataset.lesson);
            const value     = input.value.trim();

            if (!grades[studentId]) grades[studentId] = {};
            grades[studentId][lessonId] = value;

            onChange?.(studentId, lessonId, value);
        });
    }

    //действия в шапке
    if (withColumnActions) {
        container.addEventListener('click', (event) => {
            if (event.target.closest('#addLessonColBtn')) {
                onAddLesson?.();
                return;
            }
            const removeBtn = event.target.closest('[data-remove-lesson]');
            if (removeBtn) {
                const id = Number(removeBtn.dataset.removeLesson);
                const lesson = lessons.find(l => l.id === id);
                if (lesson) onRemoveLesson?.(lesson);
            }
        });
    }

    render();

    return {
        render,
        getGrades() {
            return grades;
        }
    };
}