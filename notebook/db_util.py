import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import ProgrammingError
import psycopg2.extras
from psycopg2.extras import NamedTupleCursor


class PostgresUtils:
    """
    Collection of all Postgres utility functions
    """

    def __init__(self, db_name=None, db_config=None):
        """
        Args:
            db_name: Name of database (Str) (overwrites value in db_config if present)
            db_config: Dict containing postgres server configuration
                        {'NAME': <db_name>,
                         'HOST': <host_name>,
                         'USER': <user>,
                         'PASSWORD': <pass>,
                         'PORT': <port>
                        }
        """
        #TODO: Remove the hardcoded value from here. Use env vars.
        self.db_config = {
            'NAME': 'contexalyze',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'postgres',
            'PORT': '5432'
        }
        self.conn = self.__create_new_conn__()

    def __create_new_conn__(self):
        """
        Method to connect with Postgres server
        :return: psycopg connection object with the database.
        """
        try:
            conn = psycopg2.connect(dbname=self.db_config['NAME'],
                                    user=self.db_config['USER'],
                                    host=self.db_config['HOST'],
                                    port=self.db_config['PORT'],
                                    password=self.db_config['PASSWORD'])

            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return conn
        except psycopg2.ProgrammingError as e:
            raise RuntimeError(
                    f'Error creating connection to PostgreSQL, {e})')

    def __get_connection__(self):
        """
        :return: connection if active else create new
        """
        return self.__create_new_conn__() if self.conn.closed else self.conn

    def __execute_query__(self, conn, query, fetch_after=True):
        """
        Execute given query & return result
        Args:
            conn: Postgres connection client
            query: Query to execute
            fetch_after: Execute fetchall after executing query
        Return:
            Result array
        """
        try:
            cur = conn.cursor(cursor_factory=NamedTupleCursor)
            cur.execute(query)
            result = None
            if fetch_after:
                result = cur.fetchall() if cur.rowcount > 0 else []
            cur.close()
            return result
        except ProgrammingError as e:
            raise RuntimeError('Error excuting query "%s"\n %s' % (query, e))

    def __run_query__(self, query):
        """
        handles connection to db and running the query.
        :param query:  (str) Query to execute.
        :return: Result from the query ( List )
        """
        self.conn = self.__get_connection__()
        result = self.__execute_query__(self.conn, query)
        self.conn.close()

        return result


class ExecuteQueries:
    """
    Class to write the logic of raw queries
    """

    @property
    def db(self):
        return PostgresUtils()


    def __init__(self):
        self.db


    def get_users(self):
        """
        #TODO: Remove the method if not required, this is dummy method to test the and list the connections.
        """

        result = self.db.__run_query__('select * from deming_core_enterpriseuser;')

        return result

    
    def get_mlnodes(self):
        """
        Get all the mlnodes that are in the MLNode table.
        """
        self.conn = self.db.__get_connection__()
        result = self.db.__execute_query__(self.conn, 'select * from deming_core_mlnode')

        self.conn.close()

        return result

    
    def get_ml_node(self, column_name, column_value):
        """
        Get ml node info for the given column name and value.
        :param column_name: (str) Name of the column
        :param column_value: Value of column
        :return: List of Mlnode instances.
        """
        self.conn = self.db.__get_connection__()
        result = self.db.__execute_query__(self.conn, f"select * from deming_core_mlnode where {column_name}='{column_value}'")

        self.conn.close()

        return result

    def delete_kernel_session(self, column_name, column_value):
        """
        Delete the entry in the Kernel Session table for the given column name and Value.
        :param column_name: (str) Name of the column
        :param column_value: Value of column
        """


        result = self.db.__run_query__(f"delete from deming_core_kernelsession where {column_name}='{column_value}'")

        return result


    def get_kernel_session(self, column_name, column_value):
        """
        Get ml node info for the given column name and value.
        :param column_name: (str) Name of the column
        :param column_value: Value of column
        :return: List of Mlnode instances.
        """
        result = self.db.__run_query__(f"select * from deming_core_kernelsession where {column_name}='{column_value}'")

        return result
    def create_kernel_session(self, _field_values):
        """
        Create kernel session with provided field values.
        :param _field_values: (Dict) Dictionary of field values.
        :return: result of the query.
        """
        try:
            _query = f'INSERT INTO deming_core_kernelsession(kernel_id, kernel_name) VALUES ' \
                     f'({_field_values.get("kernel_id", None)}, {_field_values.get("kernel_name", None)}, ' \
                     f'(SELECT id FROM deming_core_mlnode WHERE name = {_field_values["mlnode_name"]}))'
            print(f'_query={_query}')
            result = self.db.__run_query__(_query)
            return result

        except Exception as e:
            print(f"Exception raised ={e}")


