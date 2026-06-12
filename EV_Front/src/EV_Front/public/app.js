
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

        // 4. Obtener Conductores (NUEVO)
        const driversResponse = await fetch(`${API_BASE_URL}/drivers/`);
        const drivers = await driversResponse.json();
        renderDrivers(drivers);

        // 5. Obtener Eventos/Logs con Filtros (NUEVO)
        const ipFilter = document.getElementById('filter-ip').value.trim();
        const actionFilter = document.getElementById('filter-action').value.trim();
        
        // Construimos la URL dinámicamente según lo que haya escrito el usuario
        let eventsUrl = new URL(`${API_BASE_URL}/events/`);
        if (ipFilter) eventsUrl.searchParams.append('ip', ipFilter);
        if (actionFilter) eventsUrl.searchParams.append('action', actionFilter);

        const eventsResponse = await fetch(eventsUrl);
        const events = await eventsResponse.json();
        renderEvents(events);

    } catch (error) {
        console.error("Error connecting with API_Central:", error);
    }
}

// --- FUNCIONES DE RENDERIZADO ---

function renderCPs(cps) {
    const container = document.getElementById('cp-container');
    container.innerHTML = ''; 

    cps.forEach(cp => {
        const statusLower = cp.status.toLowerCase();
        let badgeColor = 'bg-success'; // Active / Supplying = green
        let borderColor = 'border-success';
        if (statusLower === 'stopped') { badgeColor = 'bg-warning text-dark'; borderColor = 'border-warning'; }
        if (statusLower === 'broken down') { badgeColor = 'bg-danger'; borderColor = 'border-danger'; }
        if (statusLower === 'disconnected') { badgeColor = 'bg-secondary'; borderColor = 'border-secondary'; }

        let tempWarning = cp.temperature < 0 ? '❄️ <span class="text-danger fw-bold">EXTREME COLD</span>' : '🌡️ Normal';

        // TAREA 2: Botones individuales añadidos a la tarjeta
        const card = `
            <div class="col-md-4 mb-3">
                <div class="card shadow-sm border-0 border-start border-4 ${borderColor}">
                    <div class="card-body">
                        <h5 class="card-title fw-bold">${cp.id}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">📍 ${cp.location}</h6>
                        <span class="badge ${badgeColor} mb-2">${cp.status.toUpperCase()}</span>
                        <p class="card-text mb-1">Price: ${cp.price} €/kWh</p>
                        <p class="card-text mb-3">Temp: ${cp.temperature}ºC (${tempWarning})</p>
                        
                        <div class="d-grid gap-2">
                            <div class="btn-group btn-group-sm" role="group">
                                <button type="button" class="btn btn-outline-danger" onclick="stopCP('${cp.id}')">Stop</button>
                                <button type="button" class="btn btn-outline-success" onclick="resumeCP('${cp.id}')">Resume</button>
                            </div>
                            <button type="button" class="btn btn-sm btn-outline-warning" onclick="deleteKeyCP('${cp.id}')">Delete Key</button>
                        </div>
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

    const activeOnly = document.getElementById('toggle-active-only').checked;

    transactions
        .filter(t => activeOnly ? !t.is_done : true)
        .forEach(t => {
        // TAREA 3: Inyectar t.start_date (Con fallback a 'N/A' por si el backend aún no lo envía)
        const startDate = t.start_date ? new Date(t.start_date).toLocaleString() : '<span class="text-muted">N/A</span>';
        const statusBadge = t.is_done 
            ? '<span class="badge bg-secondary">Completed</span>' 
            : '<span class="badge bg-success">In progress</span>';
        
        const row = `
            <tr>
                <td class="fw-bold">${t.id}</td>
                <td>${t.driver_id}</td>
                <td><span class="badge bg-secondary">${t.cp_id}</span></td>
                <td>${t.consumption !== null ? t.consumption : '-'}</td>
                <td>${t.price !== null ? t.price : '-'} €</td>
                <td>${startDate}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// TAREA 4: Función para renderizar los conductores
function renderDrivers(drivers) {
    const tbody = document.getElementById('drivers-body');
    tbody.innerHTML = '';

    drivers.forEach(d => {
        let statusHtml = '<span class="badge bg-success">Available</span>';
        
        // Si el backend devuelve un objeto active_supply, mostramos dónde está cargando
        if (d.active_supply) {
            statusHtml = `<span class="badge bg-primary">Charging at ${d.active_supply.cp_id}</span>`;
        }

        const row = `
            <tr>
                <td class="fw-bold">${d.id}</td>
                <td>${statusHtml}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

function renderEvents(events) {
    const container = document.getElementById('logs-container');
    container.innerHTML = '';

    events.reverse().forEach(e => {
        let logColor = "text-success";
        // Convertimos a minúsculas para hacer la búsqueda más robusta
        const actionLower = e.action.toLowerCase();
        if (actionLower.includes('error') || actionLower.includes('alert')) logColor = "text-danger";
        if (actionLower.includes('warning')) logColor = "text-warning";

        const logLine = `[${e.timestamp}] - ${e.ip} - <span class="${logColor} fw-bold">[${e.action}]</span> ${e.description}<br>`;
        container.innerHTML += logLine;
    });
}

// --- TAREA 1 Y 2: LLAMADAS A LA API PARA CONTROLES ---

async function stopAllCPs() {
    if(!confirm("Are you sure you want to STOP ALL charging points?")) return;
    try {
        await fetch(`${API_BASE_URL}/cps/stop-all`, { method: 'POST' });
        fetchData(); // Refrescar pantalla inmediatamente
    } catch (error) { console.error(error); }
}

async function resumeAllCPs() {
    try {
        await fetch(`${API_BASE_URL}/cps/resume-all`, { method: 'POST' });
        fetchData();
    } catch (error) { console.error(error); }
}

async function stopCP(id) {
    try {
        await fetch(`${API_BASE_URL}/cps/${id}/stop`, { method: 'POST' });
        fetchData();
    } catch (error) { console.error(error); }
}

async function resumeCP(id) {
    try {
        await fetch(`${API_BASE_URL}/cps/${id}/resume`, { method: 'POST' });
        fetchData();
    } catch (error) { console.error(error); }
}

async function deleteKeyCP(id) {
    if(!confirm(`Simulate encryption key loss on ${id}?`)) return;
    try {
        await fetch(`${API_BASE_URL}/cps/${id}/key`, { method: 'DELETE' });
        fetchData();
    } catch (error) { console.error(error); }
}

// Iniciar el bucle
setInterval(fetchData, 2000);
fetchData();