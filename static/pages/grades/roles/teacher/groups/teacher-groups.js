//словари
const SUBJECT_LABELS = {
    'math': 'Математика',
    'prog': 'Программирование',
    'db':   'Базы данных'
};

const LESSON_TYPE_LABELS = {
    'lesson':   'Работа на занятии',
    'homework': 'Домашняя работа',
    'control':  'Контрольная',
    'exam':     'Экзамен'
};

const GROUP_LABELS = {
    1: 'ПИЭ-23-2',
    2: 'ИВТ-22-1',
    3: 'УИ-25-5'
};

const testLessons = [
    { id: 1, groupId: 1, subject: 'prog', date: '2026-02-10', topic: 'Введение в ООП',   type: 'lesson' },
    { id: 2, groupId: 1, subject: 'prog', date: '2026-02-17', topic: 'Классы и объекты', type: 'homework' },
    { id: 3, groupId: 2, subject: 'db',   date: '2026-02-12', topic: 'Нормальные формы', type: 'control' }
];

//таблица занятий
const table = createTable(document.getElementById('lessons-body'), {
    emptyText: 'Занятий пока нет. Нажмите «Добавить занятие».',
    columns: [
        { key: 'id',      label: 'ID' },
        { key: 'groupId', label: 'Группа',  render: l => GROUP_LABELS[l.groupId] ?? l.groupId },
        { key: 'subject', label: 'Предмет', render: l => SUBJECT_LABELS[l.subject] },
        { key: 'date',    label: 'Дата' },
        { key: 'topic',   label: 'Тема' },
        { key: 'type',    label: 'Тип',     render: l => LESSON_TYPE_LABELS[l.type] }
    ],
    rows: testLessons,
    actions: [
        {
            label: 'Журнал',
            className: 'btn--primary',
            onClick: (lesson) => openJournal(lesson)
        },
        {
            label: 'Изменить',
            onClick: (lesson) => openEditModal(lesson)
        },
        {
            label: 'Удалить',
            className: 'btn--danger',
            onClick: (lesson) => removeLesson(lesson)
        }
    ]
});

//журнал
function openJournal(lesson) {
    window.location.href = `../journal/journal.html?groupId=${lesson.groupId}`;
}

const editingModal = document.getElementById('editingModal');
let editingId = null;

function openAddModal() {
    editingId = null;
    document.getElementById('editGroup').value = '1';
    document.getElementById('editSubject').value = 'math';
    document.getElementById('editDate').value = '';
    document.getElementById('editTopic').value = '';
    document.getElementById('editType').value = 'lesson';
    editingModal.classList.remove('hidden');
}

function openEditModal(lesson) {
    editingId = lesson.id;
    document.getElementById('editGroup').value = lesson.groupId;
    document.getElementById('editSubject').value = lesson.subject;
    document.getElementById('editDate').value = lesson.date;
    document.getElementById('editTopic').value = lesson.topic;
    document.getElementById('editType').value = lesson.type;
    editingModal.classList.remove('hidden');
}

function removeLesson(lesson) {
    if (!confirm(`Удалить занятие «${lesson.topic}»?`)) return;
    const newRows = table.getRows().filter(l => l.id !== lesson.id);
    table.update(newRows);
}

document.getElementById('addLessonBtn').addEventListener('click', openAddModal);
document.getElementById('cancelEdit').addEventListener('click', () => {
    editingModal.classList.add('hidden');
});

editingModal.addEventListener('submit', (event) => {
    event.preventDefault();

    const data = {
        groupId: Number(document.getElementById('editGroup').value),
        subject: document.getElementById('editSubject').value,
        date:    document.getElementById('editDate').value,
        topic:   document.getElementById('editTopic').value,
        type:    document.getElementById('editType').value
    };

    if (editingId === null) {
        const newId = Math.max(0, ...table.getRows().map(l => l.id)) + 1;
        table.update([...table.getRows(), { id: newId, ...data }]);
    } else {
        const updated = table.getRows().map(l =>
            l.id === editingId ? { ...l, ...data } : l
        );
        table.update(updated);
    }

    editingModal.classList.add('hidden');
});