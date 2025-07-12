FROM public.ecr.aws/lambda/python:3.10

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

COPY src/rest_docker/app.py .

ENV FLASK_APP=src/rest_docker/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "80"]
