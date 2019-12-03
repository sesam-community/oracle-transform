

def do_meterpoint_query(dbconnection, variables, logger, entity):
    """I'm used at Hafslund to grab readings for meterpoints from Quant
        Maintaned by Gabriell Constantin Vig
    """

    def map_quant_ifs_readings(inner_entity, inner_query_result):
        changed = False
        include_estimate = inner_entity['tmp_include_estimate']
        for key in inner_entity:
            if 'uninstalled' in key and inner_entity[key] == '0':
                if key == 'ifs-quadrantsreading:cons_uninstalled_reading':
                    result = map_query(inner_query_result, 1, include_estimate)
                    if result:
                        inner_entity['ifs-quadrantsreading:cons_uninstalled_reading'] = str(result)
                        changed = True
                elif key == 'ifs-quadrantsreading:prod_uninstalled_reading':
                    result = map_query(inner_query_result, 2, include_estimate)
                    if result:
                        inner_entity['ifs-quadrantsreading:prod_uninstalled_reading'] = str(result)
                        changed = True
                elif key == 'ifs-quadrantsreading:react_uninstalled_reading':
                    result = map_query(inner_query_result, 3, include_estimate)
                    if result:
                        inner_entity['ifs-quadrantsreading:react_uninstalled_reading'] = str(result)
                        changed = True
                elif key == 'ifs-quadrantsreading:prod_react_uninstalled_reading':
                    result = map_query(inner_query_result, 4, include_estimate)
                    if result:
                        inner_entity['ifs-quadrantsreading:react_uninstalled_reading'] = str(result)
                        changed = True
        if changed:
            inner_entity['tmp_readings_from'] = 'Quant'
        return inner_entity

    def map_query(inner_query_result, type_code, include_estimate=False):
        for r in inner_query_result:
            if r[1] and r[1] == type_code:
                if include_estimate and r[2] is not None:  # If estimate exists and we want it included
                    return r[0] + r[2]  # return summation of reading + estimate
                else:
                    return r[0]  # else return only reading
        return None

    if 'ifs-quadrantsreading:cons_uninstalled_reading' in entity:
        if entity['ifs-quadrantsreading:cons_uninstalled_reading'] == '0':
            if entity['tmp_finishdate'] is not None and entity['tmp_mch_code'] is not None:
                logger.debug('Doing query {}'.format(str(variables.query).format(**entity)))
                query_result = dbconnection.do_query(str(variables.query).format(**entity))
                for row in query_result:
                    logger.debug(f'Query returned: {row}')
                entity = map_quant_ifs_readings(inner_entity=entity, inner_query_result=query_result)
            else:
                logger.warning(f'Entity with _id : {entity["_id"]} has reading 0 but is Missing mch code or tmp_finishdate.')
    return entity
