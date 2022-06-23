# Use a locked base Python image.
FROM python:3.8.10

# Copy all required source files to the container.
WORKDIR /app

COPY ./src/ ./src
COPY ./test/ ./test

# Perform quality checks.
RUN pip install -U pip
RUN pip install -r ./src/requirements.txt

RUN python -m pytest test/t1 --doctest-modules --junitxml=junit/test-results.xml --cov=. --cov-report=xml -s
RUN python -m mypy --check-untyped-defs src
RUN python -m flake8 src --format=html --htmldir=flake-report --ignore=E501

# System-level dependencies.
USER root
RUN apt-get update -y && apt-get install build-essential python-dev -y

# Setup HTTP service for hosting our model.
ENTRYPOINT ["python", "src/main.py"]

# Expose the HTTP service on port 9999 which can be mapped by the host to a port of your choice.
EXPOSE 9999