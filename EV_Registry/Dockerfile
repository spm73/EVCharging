FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

COPY certificates/server.key certificates/server.crt certificates/ca.crt /certs/

COPY EV_Registry/ ./EV_Registry/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package EV_Registry --no-dev --frozen

EXPOSE 8000

CMD ["uv", "run", "--package", "EV_Registry", "python", "EV_Registry/src/EV_Registry/main.py"]