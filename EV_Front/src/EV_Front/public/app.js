const API_BASE_URL = window.ENV.API_URL;

async function fetchData() {
    try {
        // 1. Obtener CPs
        const cpsResponse = await fetch(`${API_BASE_URL}/cps/`);
        const cps = await cpsResponse.json();
        renderCPs(cps);

        // 2. Obtener Transacciones
        const transResponse = await fetch(`${API_BASE_URL}/transactions/`);
        const transactions = await transResponse.json();
        renderTransactions(transactions);

        // 3. Obtener Eventos/Logs
        const eventsResponse = await fetch(`${API_BASE_URL}/events/`);
        const events = await eventsResponse.json();
        renderEvents(events);

    } catch (error) {
        console.error("Error conectando con API_Central:", error);
    }
}

function renderCPs(cps) {
    const container = document.getElementById('cp-container');
    container.innerHTML = ''; // Limpiamos antes de repintar

    cps.forEach(cp => {
        // Cambiamos el color de la tarjeta según el estado
        let badgeColor = 'bg-success';
        if (cp.status === 'out_of_service') badgeColor = 'bg-danger';
        if (cp.status === 'supplying') badgeColor = 'bg-primary';

        // Alerta visual si la temperatura baja de 0 (Por si EV_W actuó)
        let tempWarning = cp.temperature < 0 ? '❄️ <span class="text-danger fw-bold">FRÍO EXTREMO</span>' : '🌡️ Normal';

        const card = `
            <div class="col-md-4 mb-3">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title">${cp.id}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">📍 ${cp.location}</h6>
                        <span class="badge ${badgeColor} mb-2">${cp.status.toUpperCase()}</span>
                        <p class="card-text mb-1">Precio: ${cp.price} €/kWh</p>
                        <p class="card-text mb-0">Temp: ${cp.temperature}ºC (${tempWarning})</p>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += card;
    });
}

function renderTransactions(transactions) {
    const tbody = document.getElementById('transactions-body');
    tbody.innerHTML = '';

    transactions.forEach(t => {
        const row = `
            <tr>
                <td>${t.id}</td>
                <td>${t.driver_id}</td>
                <td>${t.cp_id}</td>
                <td>${t.consumption}</td>
                <td>${t.price} €</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

function renderEvents(events) {
    const container = document.getElementById('logs-container');
    container.innerHTML = '';

    // Invertimos para ver los más nuevos arriba (dependiendo de cómo lo mande la BD)
    events.reverse().forEach(e => {
        // Colorear dependiendo del tipo de evento (opcional)
        let logColor = "text-success";
        if (e.action.includes('error') || e.action.includes('alert')) logColor = "text-danger";
        if (e.action.includes('warning')) logColor = "text-warning";

        const logLine = `[${e.timestamp}] - ${e.ip} - <span class="${logColor}">[${e.action}]</span> ${e.description}<br>`;
        container.innerHTML += logLine;
    });
}

// Iniciar el bucle: Refrescar todo cada 2 segundos
setInterval(fetchData, 2000);
fetchData(); // Llamada inicial inmediata