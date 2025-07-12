FROM --platform="linux/amd64" python:3.10

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

RUN apt update -y && apt upgrade -y
RUN apt install -y zip npm
RUN npm install -g aws-cdk
# Add Python and other dependencies as needed