FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY EV_Central/pyproject.toml ./EV_Central/
COPY EV_Registry/pyproject.toml ./EV_Registry/
COPY EV_CP_M/pyproject.toml ./EV_CP_M/
COPY EV_CP_E/pyproject.toml ./EV_CP_E/
COPY EV_Driver/pyproject.toml ./EV_Driver/
COPY EV_W/pyproject.toml ./EV_W/
COPY EV_Front/pyproject.toml ./EV_Front/
COPY communications/pyproject.toml ./communications/

COPY . .

RUN uv sync --frozen --no-dev

CMD ["uv", "run", "main.py"]

