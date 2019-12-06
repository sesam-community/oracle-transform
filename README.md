[![Build Status](https://travis-ci.org/sesam-community/oracle-transform.svg?branch=master)](https://travis-ci.org/sesam-community/oracle-transform)

# oracle-transform
Docker oracle integration courtesy of [egojason/docker-python-oracle](https://github.com/egojason/docker-python-oracle)
  
This docker image serves as a microservice to be used in an HTTP transform by executing queries to a database for entities.

## How to use:
### Setup environment
#### Dev phase
1. Create testing environment
    * Recommended using PyCharm with Docker integration to easily set environment variables for the container during the testing phase.
    * Otherwise set the env variables in your terminal environment and run something like 
        * ```docker build -t <your-docker-user>/httpOracle . && docker run --env db_host=$DB_HOST --env db_port=$DB_PORT --env db_database=$DB_DATABASE --env db_username=$DB_USERNAME --env db_password=$DB_PSW --env handler=$DB_HANDLER --env query=$DB_QUERY --env LOG_LEVEL=$DB_LOG_LEVEL --name httpOracle -t -i -p 5000:5000 --rm <your-dockeruser>/httpOracle```
            * Where each $DB_% is an environment variable which is available in the terminal

* !!!Setup your query to use '{key}' to grab values from the entity!
    * Like this ```SELECT * FROM A WHERE a.ID = '{_id}'```
        * This example will use the current entity's _id and pass it into the query.  
 
2. Use generic handler or Create your own handler in handlers.python
    * ```generic_handler``` returns an entity appended with the query result. This will be a list where each row is a dictionary.
    * Each handler needs the parameters: ```dbconnection, variables, logger, entity```
        * _Variables_ to get the query.
        * _dbconnection_ to run the query against.
        * _logger_ to log the errors which might be generated
        * _entity_ which is the input entity to the HTTP transform and ends up as the output of the HTTP tansform
            * I recommend only appending keys here and not removing values! You can choose which fields you want to keep in a second DTL transform.
    * Set your handler name as the environment variable 'handler' and pass it into the program.
3. Use ```curl 0.0.0.0:5000/transform -X POST -d '{"_id":"mock-data"}'``` and look at the result
    * If something goes wrong use ```docker logs httpOracle```

#### Sesam Testing Phase
1. Run the microservice inside Sesam.
 System config:
```
{
  "_id": "http-oracle-transform",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "LOG_LEVEL": "WARNING",
      "db_database": "$ENV(HTTP_ORACLE_DATABASE)",
      "db_host": "$ENV(HTTP_ORACLE_HOST)",
      "db_password": "$SECRET(HTTP_ORACLE_PASSWORD)",
      "db_port": 1521,
      "db_username": "$ENV(HTTP_ORACLE_USERNAME)",
      "handler": "generic_handler",
      "query": "SELECT address, zip FROM a WHERE a.ID = '{_id}' AND a.phone_no = '{phone_no}'"
    },
    "image": "sesamcommunity/oracle-transform:1.1.0",
    "port": 5000
  },
  "verify_ssl": true
}
```
Pipe example config
```
{
  "_id": "testing-http-transform",
  "type": "pipe",
  "source": {
    "type": "embedded",
    "entities":[{
        "_id":"im in a query wohoo",
        "phone_no": "call me maybe"
    }]
  },
  "transform": [{
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"],
        ["add", "::do_query", [<Condition-To-Do-Query>]]
      ]
    }
  }.
  {
    "type": "http",
    "system": "http-oracle-transform",
    "batch_size": 100,
    "url": "/transform"
  }, {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  }]
}
```

If the example configs where used above the microservice would put the keys from the entity into the query like this:<br>
```SELECT address, zip, subs FROM a WHERE a.ID = 'im in a query wohoo' AND a.phone_no = 'call me maybe'```<br>
and if the conditon for ```do_query == TRUE``` and the query returned for example two rows, the output would look like this:
```
{
    "_id":"im in a query wohoo",
    "phone_no": "call me maybe",
    "do_query": true
    "query_result": [
    {
        "adress": "spoofed",
        "zip": 1337
    }, {
        "adress": "MI7",
        "zip": 0007
    }]
}
```