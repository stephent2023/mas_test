FROM registry.access.redhat.com/ubi9/python-39:latest

# By default, listen on port 8080
EXPOSE 8080/tcp
ENV FLASK_PORT=8080

# Set up directories
RUN mkdir /application
WORKDIR /application

# Copy python dependencies and install these
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the applicationssd
COPY . .

# Specify the command to run on container start
CMD [ "python", "./app.py" ]
