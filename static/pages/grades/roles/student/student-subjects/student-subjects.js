//словари
const SUBJECT_LABELS = {
    'math': 'Математика',
    'prog': 'Программирование',
    'db':   'Базы данных'
};

const testSubjects = [
    { id: 'math', name: 'Математика',       teacher: 'Иванов И. И.',  lessons: 16, avg: 4.5 },
    { id: 'prog', name: 'Программирование', teacher: 'Петров П. П.',  lessons: 18, avg: 4.7 },
    { id: 'db',   name: 'Базы данных',      teacher: 'Сидорова А. В.', lessons: 12, avg: 4.3 }
];

//таблица предметов
createTable(document.getElementById('subjects-body'), {
    emptyText: 'Предметов пока нет',
    columns: [
        { key: 'name',    label: 'Предмет' },
        { key: 'teacher', label: 'Преподаватель' },
        { key: 'lessons', label: 'Занятий' },
        { key: 'avg',     label: 'Ср. балл', render: s => s.avg ?? '—' }
    ],
    rows: testSubjects,
    actions: [
        {
            label: 'Дневник',
            className: 'btn--primary',
            onClick: (subject) => openDiary(subject)
        }
    ]
});

//переход в дневник по предмету
function openDiary(subject) {
    window.location.href = `../diary/diary.html?subject=${subject.id}`;
}