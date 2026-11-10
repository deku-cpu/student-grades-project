document.addEventListener('DOMContentLoaded', function() {
    const tbody = document.getElementById('disciplines-body');
    
    // Находим фильтры
    const searchDiscipline = document.getElementById('search_discipline');
    const searchGroup = document.getElementById('search_group');
    const filterCourse = document.getElementById('filter_course');

    function loadDisciplines() {
        // Берем значения из фильтров
        let disciplineVal = searchDiscipline.value;
        let groupVal = searchGroup.value;
        let courseVal = filterCourse.value;

        
        let url = '/api/teacher/disciplines/?' + new URLSearchParams({search_discipline: disciplineVal, search_group: groupVal, course: courseVal});

        fetch(url)
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            tbody.innerHTML = ''; // Очищаем таблицу

            // Если пришла ошибка (например, не препод)
            if (!Array.isArray(data)) {
                tbody.innerHTML = '<tr><td colspan="4">Доступ ограничен</td></tr>';
                return;
            }

            // Если пусто
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4">Ничего не найдено</td></tr>';
                return;
            }

            for (let i = 0; i < data.length; i++) {
                let t = data[i];
                
                let row = '<tr>' +
                    '<td>' + escapeHtml(t.group) + '</td>' +
                    '<td>' + t.course + '</td>' +
                    '<td>' + escapeHtml(t.discipline) + '</td>' +
                    '<td><button class="btn btn--secondary" onclick="window.location.href=\'/journal/' + t.id + '/\'">Журнал</button></td>' +
                '</tr>';
                
                tbody.innerHTML += row;
            }
        })
        .catch(function(error) {
            console.error("Ошибка:", error);
        });
    }

    // Вешаем слушатели на фильтры (чтобы таблица обновлялась при вводе/выборе)
    searchDiscipline.oninput = loadDisciplines;
    searchGroup.oninput = loadDisciplines;
    filterCourse.onchange = loadDisciplines;

    // Первая загрузка при открытии страницы
    loadDisciplines();
});
