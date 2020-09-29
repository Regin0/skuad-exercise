from python:3

WORKDIR /app

COPY requirements.txt /app

RUN pip install -requirements.txt

COPY . /app

ENTRYPOINT [ "python3", "."]