def generic_handler(dbconnection, variables, logger, entity):
    """For a given entity, I query the given database and return the entity appended with 'query_result'

    :param OracleDB dbconnection: Connection to a given database.
    :param VariablesConfig variables: Object with environment variables.
    :param sesam_logger logger: Logger to log info/errors to.
    :param dict entity: Entity with keys to be used for the query.

    :returns: Entity appended with query result.
    :rtype: dict
    """
    if entity:
        entity['query_result'] = dbconnection.do_query(str(variables.query).format(**entity))
        return entity
    else:
        logger.warning(f'Input entity is None! generic_handler Returning None...')
