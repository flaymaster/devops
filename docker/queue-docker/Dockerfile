FROM public.ecr.aws/lambda/python:3.10

RUN mkdir -p /app

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

# Copy dependency files first (for better Docker caching)
COPY docker/queue-docker/pyproject.toml /app
RUN pip install --no-cache-dir boto3
# Install dependencies
RUN poetry install --no-root

# Copy your application code
COPY docker/queue-docker/src/queue_docker/app.py /app
# Set the Lambda handler
ENTRYPOINT ["python", "-u", "app.py"]
