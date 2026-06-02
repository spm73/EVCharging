# 1. Usamos una imagen oficial de Python ligera como base
FROM python:3.12-slim

# 2. Instalamos 'uv' copiándolo mágicamente desde su imagen oficial (la forma más rápida)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Creamos una carpeta dentro del contenedor donde vivirá tu código
WORKDIR /app

# 4. Copiamos los archivos de configuración del proyecto y el lockfile
# (Al estar en un workspace, copiamos desde la raíz)
COPY pyproject.toml uv.lock ./

# 5. Instalamos las dependencias súper rápido y sin basura de desarrollo
RUN uv sync --frozen --no-dev

# 6. Copiamos todo tu código (main.py, la clase Driver, etc.)
COPY . .

# 7. El comando que se ejecutará cuando el contenedor arranque
# Fíjate que no le pasamos argumentos, porque los cogerá del .env de Docker
CMD ["uv", "run", "main.py"]