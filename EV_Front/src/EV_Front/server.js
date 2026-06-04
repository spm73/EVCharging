const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Exponer la carpeta public que está al lado de este archivo
app.use(express.static(path.join(__dirname, 'public')));

// Ruta mágica para inyectar la IP del .env al HTML
app.get('/config.js', (req, res) => {
    const apiUrl = process.env.CENTRAL_API_URL || 'http://127.0.0.1:8000/api';
    res.type('.js');
    res.send(`window.ENV = { API_URL: "${apiUrl}" };`);
});

app.listen(PORT, () => {
    console.log(`[+] Frontend Web Server corriendo en http://localhost:${PORT}`);
});