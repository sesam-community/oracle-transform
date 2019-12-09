import cx_Oracle
from sesamutils.sesamlogger import sesam_logger


class OracleDB:
    def __init__(self, host, port, database, username, password):
        """
        A class used to connect to oracle databases. It automatically initiates the connection during creation.

        :param str host: Host to connect to. Either url or IP
        :param int port: Port to use for connection.
        :param str database: Database name.
        :param username: :P
        :param password: yeah...

        do_query(query): Executes the query against the database and returns all results.
        create_connection(): Initiates a connection to the database.
        """
        self.logger = sesam_logger(logger_name='Database Connection', timestamp=True)
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = self.create_connection()
        self.cursor = self.connection.cursor()

    def do_query(self, query):
        """Returns the result of the query it is passed.

        It will automatically try to re-initate the database connection if it has dropped.
            ^If this fails it will break.

        :param str query: The query to excecute.

        :returns: List of dicts where dict = row and key = column name and value = column value eg [{col_n: col_v}]
        :rtype: list(dict())
        """

        try:
            self.cursor.execute(query)
        except Exception as e:
            self.logger.warning(f'Got error "{e}".\nTrying to reconnect to Database!\n')
            self.connection = self.create_connection()
            self.cursor = self.connection.cursor()
            self.logger.warning(f'Connection successful! Trying to do query again: "{query}".')
            self.cursor.execute(query)

        # Match column names with column values to build [{column_name: column_value}, {...}, ...]
        columns = self.cursor.description
        output = []
        for row in self.cursor.fetchall():
            row_dict = {}
            for index, column_value in enumerate(row):
                row_dict[str(columns[index][0])] = str(column_value)
            output.append(row_dict)

        return output

    def create_connection(self):
        """Creates a connection to the database using object values."""
        try:
            return cx_Oracle.connect(self.username, self.password, cx_Oracle.makedsn(self.host, self.port, self.database))
        except Exception as e:
            self.logger.critical(f'Problem creating connection to database because of error "{e}"')
