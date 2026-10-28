async function loadGroups() {
    const response = await fetch('/api/groups/');
    const groups = await response.json();

    createTable(document.getElementById('groups-body'), {
        emptyText: 'Групп нет',
        columns: GROUPS_COLUMNS,
        rows: groups,
        actions: [
            {
                label: 'Журнал',
                className: 'btn--primary',
                onClick: (group) => openJournal(group)
            }
        ]
    });
}

function openJournal(group) {
    window.location.href = `../dekan-journal/dekan-journal.html?groupId=${group.id}`;
}

loadGroups();