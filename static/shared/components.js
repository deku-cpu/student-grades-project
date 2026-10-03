const role = localStorage.getItem('role');
function renderHeader(){

    let inner = ''

    inner = MENU[role].map(item => `<a href="${item.url}">${item.title}</a>`).join('');
            
    return `<header> ${inner} </header>`
}
function renderFooter(){
    return `<div>Подвал</div>` 
}