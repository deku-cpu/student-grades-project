//словари
const GROUP_LABELS = {
    1: 'ПИЭ-23-2',
    2: 'ИВТ-22-1',
    3: 'УИ-25-5'
};

const testStudents = [
    { id: 1, name: 'Абрамов И. С.' },
    { id: 2, name: 'Белова А. П.' },
    { id: 3, name: 'Волков Д. М.' },
    { id: 4, name: 'Гусева К. О.' },
    { id: 5, name: 'Дмитриев Р. В.' }
];

const testLessons = [
    { id: 101, date: '10.02', topic: 'ООП: введение',  type: 'lesson' },
    { id: 102, date: '17.02', topic: 'Классы',         type: 'lesson' },
    { id: 103, date: '24.02', topic: 'Наследование',   type: 'homework' },
    { id: 104, date: '03.03', topic: 'Контрольная №1', type: 'control' }
];

const testGrades = {
    1: { 101: '5', 102: '4', 103: '5', 104: '4' },
    2: { 101: '4', 102: '4', 103: '3' },
    3: { 101: '3', 102: '4' },
    4: { 101: '5', 102: '5', 103: '5', 104: '5' }
};

const params = new URLSearchParams(location.search);
const groupId = Number(params.get('groupId')) || null;
document.getElementById('groupLabel').value = GROUP_LABELS[groupId] ?? '—';

//таблица (только чтение)
createGradesTable(document.getElementById('grades-body'), {
    students: testStudents,
    lessons:  testLessons,
    grades:   testGrades,
    editable: false,
    withAverage: true,
    withColumnActions: false
});