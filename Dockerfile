# Use a locked base Python image.
FROM python:3.8.10 AS test
WORKDIR /app
COPY ./src ./src
COPY ./test ./test
RUN pip install -U pip
RUN pip install -r ./src/requirements.txt
RUN python -m pytest test/t1 --doctest-modules --junitxml=junit/test-results.xml --cov=. --cov-report=xml -s
RUN python -m flake8 src --format=html --htmldir=flake-report --ignore=E501
USER root
RUN apt-get update -y && apt-get install build-essential python-dev -y

FROM python:3.8.10 AS app
WORKDIR /app
COPY --from=test /app/src .
RUN pip install -r ./requirements.txt
ENTRYPOINT ["python", "main.py"]
EXPOSE 9999