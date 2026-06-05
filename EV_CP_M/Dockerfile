FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY EV_Central/pyproject.toml ./EV_Central/
COPY EV_Registry/pyproject.toml ./EV_Registry/
COPY EV_CP_M/pyproject.toml ./EV_CP_M/
COPY EV_CP_E/pyproject.toml ./EV_CP_E/
COPY EV_Driver/pyproject.toml ./EV_Driver/
COPY EV_W/pyproject.toml ./EV_W/
COPY EV_Front/pyproject.toml ./EV_Front/
COPY communications/pyproject.toml ./communications/

COPY communications/ ./communications/
COPY EV_CP_M/ ./EV_CP_M/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package EV_CP_M --no-dev --frozen

COPY certificates/ca.crt ./EV_CP_M/src/certs/

WORKDIR /app/EV_CP_M/src

CMD ["uv", "run", "--package", "EV_CP_M", "python", "-m", "EV_CP_M.main"]

