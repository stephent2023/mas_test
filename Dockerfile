# Inherit python image
FROM registry.access.redhat.com/ubi9/python-39:latest

# Set up directories
WORKDIR /projects

# Virtual env
RUN python -m pip install virtualenv
RUN python -m venv venv
RUN venv/Scripts/activate

# Copy python dependencies and install these
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the applicationssd
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED 1

# EXPOSE port 8081 to allow communication to/from server
EXPOSE 8001
STOPSIGNAL SIGINT

# RUN the python script
ENTRYPOINT ["python"]
CMD ["flaskapi.py"]
