FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY certificates/server.key certificates/server.crt certificates/ca.crt /certs/

COPY communications/pyproject.toml ./communications/
COPY EV_Central/pyproject.toml ./EV_Central/
COPY EV_CP_M/pyproject.toml ./EV_CP_M/
COPY EV_CP_E/pyproject.toml ./EV_CP_E/

COPY EV_Registry/ ./EV_Registry/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package EV_Registry --no-dev --frozen

EXPOSE 8000
WORKDIR /app/EV_Registry/src

CMD ["uv", "run", "--package", "EV_Registry", "python", "-m", "EV_Registry.main"]