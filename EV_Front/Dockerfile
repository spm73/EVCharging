# Usamos una versión oficial y ligera de Node.js
FROM node:20-alpine

# Creamos la carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el package.json y descargamos las dependencias
RUN npm install

# Copiamos el resto del código (tu carpeta src y sus archivos)

# Exponemos el puerto estandarizado
EXPOSE 3000

# Comando de arranque (Node leerá las variables inyectadas automáticamente)
CMD ["node", "src/EV_Front/server.js"]

COPY pyproject.toml uv.lock ./
COPY EV_Central/pyproject.toml ./EV_Central/
COPY EV_Registry/pyproject.toml ./EV_Registry/
COPY EV_CP_M/pyproject.toml ./EV_CP_M/
COPY EV_CP_E/pyproject.toml ./EV_CP_E/
COPY EV_Driver/pyproject.toml ./EV_Driver/
COPY EV_W/pyproject.toml ./EV_W/
COPY EV_Front/pyproject.toml ./EV_Front/
COPY communications/pyproject.toml ./communications/

COPY package.json ./
COPY . .

