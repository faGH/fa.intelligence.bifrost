# Use the base image from Freqtrade.
FROM freqtradeorg/freqtrade:2021.9

# Copy all required source files to the container.
WORKDIR /app

COPY ./src/ ./

# System-level dependencies.
USER root
RUN apt-get update -y && apt-get install build-essential python-dev -y

# Install PIP dependencies for the web service.
RUN pip install -U pip
RUN pip install -U flask
RUN pip install -U flask_restx

# Install PIP dependencies for the Prophet library.
#RUN pip install -U -r requirements.prophet.txt
RUN pip install -U pymeeus ujson korean-lunar-calendar hijri-converter ephem convertdate setuptools-git LunarCalendar holidays cmdstanpy
RUN pip install -U pystan==2.19.1.1
RUN pip install -U prophet

# Setup HTTP service for hosting our model.
ENTRYPOINT ["python", "main.py"]

# Expose the HTTP service on port 9999 which can be mapped by the host to a port of your choice.
EXPOSE 9999