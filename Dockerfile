# Inherit python image
FROM registry.access.redhat.com/ubi9/python-39:latest

# Set up directories
WORKDIR /projects

# Copy python dependencies and install these
COPY requirements.txt .
RUN pip install -r requirements.txt
#RUN python -m pip install virtualenv
#RUN python -m venv venv
#RUN venv/Scripts/activate
#RUN pip install flask_restful
RUN pip install flask-mysql
#RUN pip install flask-restx
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
