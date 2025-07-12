FROM public.ecr.aws/lambda/python:3.10

RUN mkdir -p /app

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

COPY docker/rest-docker/pyproject.toml ./

# Install dependencies
RUN poetry install --no-root

COPY docker/rest-docker/src/rest_docker/app.py .

ENV FLASK_APP=docker/rest-docker/src/rest_docker/app.py 
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "80"]
ENTRYPOINT ["python", "-u", "app.py"]