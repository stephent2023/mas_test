# MAS flask API
This app creates an API used to send and recieve monitoring data to a MySQL database
Developed  for use in openshift

Deploy through the openshift CLI with the following commands:
```
oc new-app https://github.com/stephent2023/mas_test --name="api"
oc expose service/api --port=8001
```

The API needs environmental variables to connect to the DB, named as follows:
```
DB_USER       DB_PASS       DB_NAME       DB_ENDPOINT
```
