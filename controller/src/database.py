'''Database connector class. Singleton with pool.'''
from psycopg2 import pool
#TODO use asyncpg instead psycopg2

from .settings import DATABASE

class DatabaseConnection:
    '''Connector to PostgreSQL'''
    _instance = None

    def __new__(cls, connection_name='default'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # TODO level
            user=DATABASE.get(connection_name, '{}').get('LOGIN', '')
            host=DATABASE.get(connection_name, '{}').get('HOST', '')
            database=DATABASE.get(connection_name, '{}').get('NAME', '')
            pool_size=DATABASE.get('poolSize', 5)
            print(f"Connecting to {user}@{host}/{database} with {pool_size} poolsize")
            cls._pool = pool.SimpleConnectionPool(
                1,
                pool_size,
                host=host,
                database=database,
                user=user,
                password=DATABASE.get(connection_name, '{}').get('PASSWORD', '')
            )
        return cls._instance

    def __enter__(self):
        self.connection = self._pool.getconn()
        return self

    def __exit__(self, type, value, traceback):
        #Exception handling here
        self._pool.putconn(self.connection)

    @classmethod
    def get_connection(cls):
        '''Return session from pool'''
        return cls._pool.getconn()

    @classmethod
    def release_connection(cls, connection):
        '''Return session to pool'''
        return cls._pool.putconn(connection)
