# Use Python 3.12 slim as the base image
FROM python:3.12-slim

# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency configuration files
COPY pyproject.toml uv.lock ./

# Install project dependencies (excluding development dependencies)
RUN uv sync --frozen --no-dev --no-install-project

# Copy package source code and metadata files
COPY README.md ./
COPY organizer/ ./organizer/

# Install the project itself (without dev dependencies)
RUN uv sync --frozen --no-dev

# Create a non-root user and change ownership of the work directory
RUN useradd -u 10001 -m organizer && \
    chown -R organizer:organizer /app

# Switch to the non-root user
USER organizer

# Set path to include the virtual environment bin
ENV PATH="/app/.venv/bin:$PATH"

# Run doctor check as the default command
CMD ["file-organizer", "doctor"]
