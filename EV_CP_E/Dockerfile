FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copiar archivos base de uv
COPY pyproject.toml uv.lock ./

# Copiar los pyproject de otros servicios para evitar errores de validación de workspace en uv
COPY EV_Central/pyproject.toml ./EV_Central/
COPY EV_Registry/pyproject.toml ./EV_Registry/
COPY EV_CP_M/pyproject.toml ./EV_CP_M/

# Copiar la dependencia compartida
COPY communications/ ./communications/

# Copiar el código fuente del Engine
COPY EV_CP_E/ ./EV_CP_E/

# Sincronizar entorno virtual únicamente con lo necesario para el Engine
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package EV_CP_E --no-dev --frozen

# Exponer el puerto por el que escucha el SocketServer (9000 por defecto)
EXPOSE 9000

# Situarnos en la carpeta src para que los imports absolutos enganchen bien
WORKDIR /app/EV_CP_E/src

# Arrancar el main como módulo
CMD ["uv", "run", "--package", "EV_CP_E", "python", "-m", "EV_CP_E.main"]
