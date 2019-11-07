import cx_Oracle
from sesamutils.sesamlogger import sesam_logger


class OracleDB:
    def __init__(self, host, port, database, username, password):
        """
        A class used to connect to oracle databases
        It automatically initiates the connection during creation.
        ...

        Attributes
        ----------
        host : str
            host url or IP
        port : int
            Standard 1521, but can variate.
        database : str
            The database name
        username : str
        password : str

        Methods
        -------
        do_query(query)
            Excecutes the query against the database and returns all results.

        create_connection()
            Initiates a connection to the database.

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

        Does not support None as query.
        It will automatically try to re-initate the database connection if the first try fails.
        If this fails it will break.

        Parameters
        ----------
        query : str
            the query to excecute

        Returns
        -------
        list(list())
            Each element of the list returned is a row.
            Each row is a list of the column values returned by the query.
        """

        try:
            self.cursor.execute(query)
        except Exception as e:
            self.logger.warning(f'Got error "{e}".\nTrying to reconnect to Database!\n')
            self.connection = self.create_connection()
            self.cursor = self.connection.cursor()
            self.logger.warning(f'Trying to do query again: "{query}".')
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def create_connection(self):
        """Creates a connection to the database using object values."""
        try:
            return cx_Oracle.connect(self.username, self.password, cx_Oracle.makedsn(self.host, self.port, self.database))
        except Exception as e:
            self.logger.critical(f'Problem creating connection to database because of error "{e}"')
