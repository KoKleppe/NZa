# NZa
code assignment

## Project Description
This project revolves around retrieving data from a SOAP service and storing this into a MySQL database hosted by docker

## Getting started 
### Run a MySQL database using docker
```bash
docker run -d -p 3306:3306 \
--name mysql-docker-container \
-e MYSQL_ROOT_PASSWORD=<your_password> \
-e MYSQL_DATABASE=<your_db> \
-e MYSQL_USER=<your_username> \
-e MYSQL_PASSWORD=<your_password \
mysql/mysql-server:latest
```
### Create a db_config.json with database information/credentials
```json
{
    "host": <your_hostname>,
    "user": <your_username>,
    "passwd": <your_password>,
    "db": <your_db>
}
```

### Run the python script, specifying the db_config.json location (default is adjacent to the python script (SOAP2MySQL))
```python
python SOAP2MySQL --config db_config.json
``` 

## Example output
![example_output](https://github.com/KoKleppe/NZa/assets/27730191/60fbb2d1-932f-4ed4-973c-54a98052db4c)

## Prerequisites
* Python (3.10.11)
* Docker (version 26.0.0, build 2ae903e)
* zeep (4.2.1)
* mysqlclient (2.2.4)

## Author
Ko Kleppe
