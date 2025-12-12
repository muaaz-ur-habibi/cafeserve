

document.addEventListener('DOMContentLoaded', function () {
    console.log("Starting dash update");

    function updateDash() {
        fetch('/api/get_server_stats')
        .then(response => response.json())
        .then(data =>{
            document.getElementById("server-stats-memory").textContent = `Memory: ${data.memory_info} GB`;
            document.getElementById("server-stats-netio").textContent = `Net IO: ${data.network_info}`;
            document.getElementById("server-stats-battery").textContent = data.battery;
            document.getElementById("server-stats-database_size").textContent = data.database_size;
        })
        .catch(error => {
            console.error("ERROR FETCHING DATA", error)
        })
    }

    const updateInterv = setInterval(updateDash, 5000);
    updateDash();

    window.addEventListener('beforeunload', function() {
        clearInterval(updateInterv);
    })
})