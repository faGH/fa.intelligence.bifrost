# Use the Conda base image to build a Python web app.
FROM continuumio/miniconda3

# Copy all required source files to the container.
WORKDIR /app

COPY ./src/ ./
COPY ./.environments/ ./

# Setup Conda environment according to the environment spec file.
RUN conda env create -f conda.yaml
SHELL ["conda", "run", "-n", "container-environment", "/bin/bash", "-c"]

# Install additional PIP packages in the context of the created Conda environment, if required.
#RUN pip install -U ...

# Setup HTTP service for hosting our model.
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "container-environment", "python", "main.py"]

# Expose the HTTP service on port 9999 which can be mapped by the host to a port of your choice.
EXPOSE 9999