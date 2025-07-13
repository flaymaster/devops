FROM public.ecr.aws/lambda/python:3.10

RUN mkdir -p /app

WORKDIR /app

RUN pip install --no-cache-dir flask boto3

COPY docker/rest-docker/src/rest_docker/app.py /app

ENV FLASK_APP=/app/app.py 
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80

ENTRYPOINT ["flask", "run", "-p", "80:80",'-host', "0.0.0.0"]
