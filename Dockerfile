# syntax=docker/dockerfile:1

# Build static files
FROM node:24-slim AS node_builder

# Working directory
WORKDIR /app

# Copy everything related to static files
COPY ./jstoolchain/ ./jstoolchain/
COPY ./templates/ ./templates/
COPY ./static/ ./static/

# Build css and js
RUN cd jstoolchain && npm ci && npm run tailwind-build && npm run js-build

# Build python project
FROM python:3.12.8 AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Working directory
WORKDIR /app

# Copy build context files
ADD . .

# Copy over static files from previous stage
COPY --from=node_builder /app/static/ ./static/

# Install dependencies (do not install project yet for better caching
# https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable


# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# Create a new user 'user' and give it sudo privileges (running as root is considered a security risk)
RUN useradd -m user && echo "user:user" | chpasswd && adduser user sudo

# Ensure ownership and permissions
RUN chown -R user:user /app && \
    chmod +x ./scripts/startup_django.sh

# Switch to 'user'
USER user

# Document that the django server will run on port 8000
EXPOSE 8000

# Sepcify start command
CMD ["uv", "run", "scripts/startup_django.sh"]