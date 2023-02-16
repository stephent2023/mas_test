
# Inherit python image
FROM registry.access.redhat.com/ubi9/python-39:latest

# Set up directories
WORKDIR /projects

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
CMD ["test.py"]
