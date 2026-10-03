const SUBJECT_LABELS = {
    'math': 'Математика',
    'prog': 'Программирование',
    'db':   'Базы данных'
};

const SUBJECT_ROWS = [
    { id: 'math', name: 'Математика' },
    { id: 'prog', name: 'Программирование' },
    { id: 'db',   name: 'Базы данных' }
];

const testLessons = [
    { id: 101, subject: 'prog', date: '10.02', topic: 'ООП: введение' },
    { id: 102, subject: 'prog', date: '17.02', topic: 'Классы' },
    { id: 103, subject: 'math', date: '11.02', topic: 'Производные' },
    { id: 104, subject: 'math', date: '18.02', topic: 'Интегралы' },
    { id: 105, subject: 'db',   date: '12.02', topic: 'Нормальные формы' },
    { id: 106, subject: 'db',   date: '19.02', topic: 'SQL-запросы' }
];

const testGrades = {
    prog: { 101: '5', 102: '4' },
    math: { 103: '4', 104: '5' },
    db:   { 105: '5', 106: '4' }
};

const params = new URLSearchParams(location.search);
const urlSubject = params.get('subject');

document.getElementById('filterSubject').value = urlSubject ?? '';

const container = document.getElementById('grades-body');

function render(subjectFilter) {
    const lessons = subjectFilter
        ? testLessons.filter(l => l.subject === subjectFilter)
        : testLessons;

    const subjects = subjectFilter
        ? SUBJECT_ROWS.filter(s => s.id === subjectFilter)
        : SUBJECT_ROWS;

    const grades = {};
    subjects.forEach(s => {
        grades[s.id] = {};
        lessons.forEach(l => {
            if (l.subject !== s.id) return;
            const v = testGrades[s.id]?.[l.id];
            if (v) grades[s.id][l.id] = v;
        });
    });

    container.innerHTML = '';

    createGradesTable(container, {
        students: subjects,
        lessons:  lessons,
        grades:   grades,
        editable: false,
        withAverage: true,
        withColumnActions: false,
        firstColumnLabel: 'Предмет'
    });
}

document.getElementById('filterSubject').addEventListener('change', (e) => {
    const value = e.target.value || null;
    render(value);
    const newUrl = value ? `?subject=${value}` : location.pathname;
    history.replaceState(null, '', newUrl);
});

render(urlSubject);