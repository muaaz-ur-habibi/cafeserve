document.addEventListener('DOMContentLoaded', function () {
    function updateAdmin() {
        fetch('/api/get_users_count')
        .then(response => response.json())
        .then(data =>{
            document.getElementById("users-count").textContent = `Logged in users: ${data.users_count}`;
        })
        .catch(error => {
            console.error("ERROR FETCHING DATA", error)
        })
    }

    const updateInterv = setInterval(updateAdmin, 5000);
    updateAdmin();

    window.addEventListener('beforeunload', function() {
        clearInterval(updateInterv);
    })
})