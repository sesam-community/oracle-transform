from flask import Flask, Response, request
import json
import sys

#local imports
from oracle_connection import OracleDB
import handlers

#sesamutils
from sesamutils.variables import VariablesConfig
from sesamutils.sesamlogger import sesam_logger
from sesamutils.flask import serve

app = Flask(__name__)


def stream_json(testing):
    first = True
    yield '['
    for i, row in enumerate(testing):
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(row)
    yield ']'

@app.route('/transform', methods=['POST'])
def receiver():
    """This function iterates over input entities and returns the handled version.
    To use this properly add your own method inside handlers.py, and specify this method as the env variable 'handler'
    Make sure your handler skips entities which do not need the query…
    """
    # get entities from request
    req_entities = request.get_json()
    output = []
    try:
        for entity in req_entities:
            handler = getattr(handlers, variables.handler)
            entity = handler(databaseConnection, variables, logger, entity)
            logger.debug(f'Appending entity: {json.dumps(entity)} to output!')
            output.append(entity)
    except TypeError as e:
        logger.critical('Wrong type gave error: {}'.format(e))
    except Exception as e:
        logger.critical(f'Error when handling entities:\n{json.dumps(req_entities)}\nError message:\n{e}')

    # Generate the response
    try:
        return Response(stream_json(output),
                        mimetype='application/json')
    except BaseException as e:
        return Response(status=500, response=f"An error occured during transform of input. Error: {e}")


if __name__ == '__main__':
    variables = VariablesConfig(
        ['db_host', 'db_port', 'db_database', 'db_username', 'db_password', 'handler', 'query', 'LOG_LEVEL'])
    if not variables.validate():
        sys.exit(-1)

    databaseConnection = OracleDB(host=variables.db_host, port=variables.db_port, database=variables.db_database,
                                  username=variables.db_username,
                                  password=variables.db_password)
    logger = sesam_logger(logger_name='SQL_TRANSFORM', timestamp=True, app=app)
    serve(app=app)
