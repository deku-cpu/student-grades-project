const testGroups = [
    {
        id: 1,
        name: 'ПИЭ-23-2',
        yearOfStudy: 3,
        specialty: 'Прикладная информатика в экономике',
        form: 'full-time',
        admissionYear: 2023,
        students: 23
    },
    {
        id: 2,
        name: 'ИВТ-22-1',
        yearOfStudy: 4,
        specialty: 'Информатика и вычислительная техника',
        form: 'part-time',
        admissionYear: 2022,
        students: 42
    },
    {
        id: 3,
        name: 'УИ-25-5',
        yearOfStudy: 2,
        specialty: 'Управление информацией',
        form: 'distance_learning',
        admissionYear: 2025,
        students: 32
    }
];

const table = createTable(document.getElementById('groups-body'), {
    emptyText: 'Групп нет',
    columns: GROUPS_COLUMNS,
    rows: testGroups,
    actions: [
        {
            label: 'Журнал',
            className: 'btn--primary',
            onClick: (group) => openJournal(group)
        }
    ]
});

function openJournal(group) {
    window.location.href = `../dekan-journal/dekan-journal.html?groupId=${group.id}`;
}