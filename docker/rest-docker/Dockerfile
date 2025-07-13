FROM python:3.10

WORKDIR /app

# Install Poetry

RUN pip install poetry

# Copy dependency files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-root

# Copy your application code
COPY src/rest_docker/ ./rest_docker/

# Set the entrypoint (adjust as needed)
CMD ["poetry", "run", "python", "-m", "rest_docker.app"]