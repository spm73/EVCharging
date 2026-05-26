FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy workspace config files needed for uv to resolve the workspace
COPY pyproject.toml uv.lock ./

# Copy only the packages EV_CP_M depends on
COPY communications/ communications/
COPY EV_CP_M/ EV_CP_M/

# Install only EV_CP_M and its dependencies (no dev deps, no other workspace members)
RUN uv sync --package ev-cp-m --no-dev

WORKDIR /app/EV_CP_M

CMD ["uv", "run", "--package", "ev-cp-m", "python", "-m", "src.EV_CP_M.main"]