# 1. Usamos la versión de Node.js
FROM node:20-alpine

# 2. Creamos la carpeta de trabajo
WORKDIR /app

# 3. PRIMERO copiamos la lista de la compra de JS
COPY package.json ./

# 4. LUEGO instalamos las dependencias (ahora sí encontrará el package.json)
RUN npm install

# 5. DESPUÉS copiamos todo tu código fuente del frontend
COPY . .

# 6. Abrimos el puerto de la web
EXPOSE 3000

# 7. Arrancamos el servidor
CMD ["node", "src/EV_Front/server.js"]