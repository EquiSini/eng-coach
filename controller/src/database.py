'''Database connector class. Singleton with pool.'''
from psycopg2 import pool

from .settings import DATABASE


class DatabaseConnection:
    '''Connector to PostgreSQL'''
    _instance = None

    def __new__(cls, connection_name='default'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # TODO level
            print("Connecting to {user}@{host}/{db} with {pool} poolsize".format(
                user=DATABASE.get(connection_name, '{}').get('LOGIN', ''),
                host=DATABASE.get(connection_name, '{}').get('HOST', ''),
                db=DATABASE.get(connection_name, '{}').get('NAME', ''),
                pool=DATABASE.get('poolSize', 5),
            ))
            cls._pool = pool.SimpleConnectionPool(
                1,
                DATABASE.get('poolSize', 5),
                host=DATABASE.get(connection_name, '{}').get('HOST', ''),
                database=DATABASE.get(connection_name, '{}').get('NAME', ''),
                user=DATABASE.get(connection_name, '{}').get('LOGIN', ''),
                password=DATABASE.get(connection_name, '{}').get('PASSWORD', '')
            )
        return cls._instance

    @classmethod
    def get_connection(cls):
        '''Return session from pool'''
        return cls._pool.getconn()
