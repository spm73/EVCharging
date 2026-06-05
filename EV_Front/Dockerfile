# Usamos una versión oficial y ligera de Node.js
FROM node:20-alpine

# Creamos la carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el package.json y descargamos las dependencias
COPY package.json ./
RUN npm install

# Copiamos el resto del código (tu carpeta src y sus archivos)
COPY . .

# Exponemos el puerto estandarizado
EXPOSE 3000

# Comando de arranque (Node leerá las variables inyectadas automáticamente)
CMD ["node", "src/EV_Front/server.js"]