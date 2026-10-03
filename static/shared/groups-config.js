const FORM_LABELS = {
    'full-time': 'Очная',
    'part-time': 'Заочная',
    'distance_learning': 'Дистанционная'
};

const GROUPS_COLUMNS = [
    { key: 'id',            label: 'ID' },
    { key: 'name',          label: 'Название' },
    { key: 'yearOfStudy',   label: 'Курс' },
    { key: 'specialty',     label: 'Специальность' },
    { key: 'form',          label: 'Форма', render: g => FORM_LABELS[g.form] },
    { key: 'admissionYear', label: 'Год' },
    { key: 'students',      label: 'Студентов' }
];