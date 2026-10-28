document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logoutBtn');
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            fetch('/api/logout/', { method: 'POST' })
            .then(function(response) {
                if (response.ok) {
                    localStorage.removeItem('role');
                    window.location.href = '/login/';
                }
            });
        });
    }
});