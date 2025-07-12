FROM public.ecr.aws/lambda/python:3.10

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

# Copy dependency files first (for better Docker caching)
COPY pyproject.toml ./

# Install dependencies
RUN poetry install --no-root

# Copy your application code
COPY src/queue_docker/app.py ./queue_docker/app.py

# Set the Lambda handler
CMD ["queue_docker.app.lambda_handler"]
