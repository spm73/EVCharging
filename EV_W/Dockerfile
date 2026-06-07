FROM python:3.12-slim

# Instalamos uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Optimizaciones
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# ==========================================
# LA CLAVE: Le decimos a Linux que active y use el entorno virtual bueno
ENV PATH="/app/.venv/bin:$PATH"
# ==========================================

# 1. Copiamos la configuración global
COPY pyproject.toml uv.lock ./

# 2. El esqueleto de todos los módulos
COPY EV_Driver/pyproject.toml ./EV_Driver/
COPY EV_Front/pyproject.toml ./EV_Front/
COPY EV_W/pyproject.toml ./EV_W/
COPY EV_Central/pyproject.toml ./EV_Central/
COPY EV_Registry/pyproject.toml ./EV_Registry/
COPY EV_CP_E/pyproject.toml ./EV_CP_E/
COPY EV_CP_M/pyproject.toml ./EV_CP_M/

# 3. Copiamos las carpetas reales necesarias
COPY communications/ ./communications/
COPY EV_Central/ ./EV_Central/
COPY EV_W/ ./EV_W/

# 4. Instalamos las dependencias en /app/.venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package ev-w --no-dev --frozen

# 5. Nos metemos en la carpeta src
WORKDIR /app/EV_W/src

# 6. Arrancamos Python de forma NATIVA (sin uv)
CMD ["python", "-m", "EV_W.main"]