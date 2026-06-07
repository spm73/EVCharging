FROM python:3.12-slim

# Instalamos uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Optimizaciones de uv para Docker
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 1. Copiamos la lista de la compra global
COPY pyproject.toml uv.lock ./

# 2. Copiamos el archivo de configuración exclusivo de tu módulo
COPY EV_Driver/pyproject.toml ./EV_Driver/

# 3. Copiamos el módulo de comunicaciones entero (como hace tu compañero)
COPY communications/ ./communications/

# 4. Instalamos dependencias usando la caché mágica.
# Al usar --package ev-driver, uv prepara tu módulo y detecta 'communications'
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package ev-driver --no-dev --frozen

# 5. Copiamos el resto de tu código fuente
COPY EV_Driver/ ./EV_Driver/

# 6. Nos metemos en la carpeta src (tal y como hace él)
WORKDIR /app/EV_Driver/src

# 7. Arrancamos tu programa como un módulo nativo de Python
CMD ["uv", "run", "--package", "ev-driver", "python", "-m", "EV_Driver.main"]