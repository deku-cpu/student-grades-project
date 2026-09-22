const FORM_LABELS = {
    'full-time': 'Очная',
    'part-time': 'Заочная',
    'distance_learning': 'Дистанционная'
};
const testGroups = [

    {

        id: 1,
        name: "ПИЭ-23-2",
        yearOfStudy: 3,
        specialty: "Прикладная информатика в экономике", // эти получется тоже предопредлены ... пупупупупу
        form: "full-time",//ПРЕДОПРЕДЕЛЕНО
        admissionYear: 2023,
        students: 23,

    },
    {
        id: 2,
        name: "ИВТ-22-1",
        yearOfStudy: 4,
        specialty: "ИВТ ИВТ ИВТИВТИВТИВТИВТИ",
        form: "part-time",
        admissionYear: 2022,
        students: 42,

    },
    {
        id: 3,
        name: "УИ-25-5",
        yearOfStudy: 2,
        specialty: "пупупупупупупупупупу",
        form: "distance_learning",
        admissionYear: 2025,
        students: 32,

    }

]  


function renderGroups(groups){
    const tbody = document.getElementById("groups-body");
    const rows = testGroups.map(g => `<tr>
    <td>${g.id}</td>
    <td>${g.name}</td>
    <td>${g.yearOfStudy}</td>
    <td>${g.specialty}</td>
    <td>${FORM_LABELS[g.form]}</td>
    <td>${g.admissionYear}</td>
    <td>${g.students}</td>
    <td><button class="btn btn--secondary" data-id="${g.id}">Изменить</button></td>
    </tr>`).join('');
    
    tbody.addEventListener('click', (event) => {
        const button = event.target.closest('button');
        if (!button) return;

        const id = Number(button.dataset.id);
        const group = testGroups.find(g => g.id === id);
        const editForm = document.getElementById("editingModal")
        editForm.classList.remove('hidden');
        document.getElementById("editName").value = group.name
        document.getElementById("editYearOfStudy").value = group.yearOfStudy
        document.getElementById("editSpecialization").value = group.specialty
        document.getElementById("editForm").value = group.  
        document.getElementById("editAdmissionYear").value = group.admissionYear
        document.getElementById("editStudentCount").value = group.students

    });
    
    tbody.innerHTML = rows;
}
renderGroups(testGroups);

