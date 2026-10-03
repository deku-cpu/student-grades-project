let testStudents = [
    { id: 1, name: 'Абрамов И. С.' },
    { id: 2, name: 'Белова А. П.' },
    { id: 3, name: 'Волков Д. М.' },
    { id: 4, name: 'Гусева К. О.' },
    { id: 5, name: 'Дмитриев Р. В.' }
];

let testLessons = [
    { id: 101, date: '10.02', topic: 'ООП: введение', type: 'lesson' },
    { id: 102, date: '17.02', topic: 'Классы',        type: 'lesson' },
    { id: 103, date: '24.02', topic: 'Наследование',  type: 'homework' },
    { id: 104, date: '03.03', topic: 'Контрольная №1', type: 'control' }
];

let testGrades = {
    1: { 101: '5', 102: '4', 103: '5', 104: '4' },
    2: { 101: '4', 102: '4', 103: '3' },
    3: { 101: '3', 102: '4' },
    4: { 101: '5', 102: '5', 103: '5', 104: '5' }
};

const gradesTable = createGradesTable(document.getElementById('grades-body'), {
    students: testStudents,
    lessons:  testLessons,
    grades:   testGrades,
    editable: true,
    withAverage: true,
    withColumnActions: true,
    onChange: (studentId, lessonId, value) => {
        console.log('Оценка обновлена:', { studentId, lessonId, value });
        // TODO: api.saveGrade(...)
    },
    onAddLesson: () => openLessonModal(),
    onRemoveLesson: (lesson) => {
        if (!confirm(`Удалить колонку «${lesson.topic}»?`)) return;
        testLessons = testLessons.filter(l => l.id !== lesson.id);
        // чистим оценки по этому занятию
        Object.values(testGrades).forEach(row => delete row[lesson.id]);
        refreshTable();
    }
});

function refreshTable() {

    document.getElementById('grades-body').innerHTML = '';
    createGradesTable(document.getElementById('grades-body'), {
        students: testStudents,
        lessons:  testLessons,
        grades:   testGrades,
        editable: true,
        withAverage: true,
        withColumnActions: true,
        onChange: (studentId, lessonId, value) => {
            console.log('Оценка обновлена:', { studentId, lessonId, value });
        },
        onAddLesson: () => openLessonModal(),
        onRemoveLesson: (lesson) => {
            if (!confirm(`Удалить колонку «${lesson.topic}»?`)) return;
            testLessons = testLessons.filter(l => l.id !== lesson.id);
            Object.values(testGrades).forEach(row => delete row[lesson.id]);
            refreshTable();
        }
    });
}

const lessonModal = document.getElementById('lessonModal');

function openLessonModal() {
    document.getElementById('lessonDate').value = '';
    document.getElementById('lessonTopic').value = '';
    document.getElementById('lessonType').value = 'lesson';
    lessonModal.classList.remove('hidden');
}

document.getElementById('addLessonBtn').addEventListener('click', openLessonModal);
document.getElementById('cancelLesson').addEventListener('click', () => {
    lessonModal.classList.add('hidden');
});

lessonModal.addEventListener('submit', (event) => {
    event.preventDefault();

    const date  = document.getElementById('lessonDate').value; // '2026-03-10'
    const topic = document.getElementById('lessonTopic').value.trim();
    const type  = document.getElementById('lessonType').value;

    if (!date || !topic) return;

    const [, mm, dd] = date.split('-');
    const shortDate = `${dd}.${mm}`;

    const newId = Math.max(0, ...testLessons.map(l => l.id)) + 1;
    testLessons.push({ id: newId, date: shortDate, topic, type });

    lessonModal.classList.add('hidden');
    refreshTable();
});