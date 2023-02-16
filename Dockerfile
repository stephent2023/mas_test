
# Inherit python image
FROM python:3.6-slim

# Set up directories
RUN mkdir /application
WORKDIR /application

# Copy python dependencies and install these
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy the rest of the applicationssd
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED 1

# EXPOSE port 8081 to allow communication to/from server
EXPOSE 8081
STOPSIGNAL SIGINT

ENTRYPOINT ["python"]
CMD ["hellowrldflask.py"]
