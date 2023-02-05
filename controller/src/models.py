'''Model classes'''
from pydantic import BaseModel
from .database import DatabaseConnection

#CONSTS
INSERT_USER_QUERY = "INSERT INTO eng_user (name, surname) VALUES (%s, %s) RETURNING id"
SELECT_USER_QUERY = "SELECT id, name, surname FROM eng_user WHERE id = %s"
UPDATE_USER_QUERY = "UPDATE eng_user SET name=%s, surname=%s WHERE id=%s"
DELETE_USER_QUERY = "DELETE FROM eng_user WHERE id = %s"


class User(BaseModel):
    '''User dataclass'''
    id: int = 0
    name: str
    surname: str
    # pass: str pbkdf2 python

class NoDataFoundError(Exception):
    '''Class for no data errors'''
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
    
#TODO Split model and recieving
class UserProducer:
    '''Producer of user objects'''
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create(self, name:str, surname:str) -> User:
        """Create a new user"""
        connection = DatabaseConnection().get_connection()
        cursor = connection.cursor()
        cursor.execute(INSERT_USER_QUERY, (name, surname))
        result = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return User(id=result[0], name=name, surname=surname)

    def read(self, user_id:int) -> User:
        """Get a user by id"""
        connection = DatabaseConnection().get_connection()
        cursor = connection.cursor()
        cursor.execute(SELECT_USER_QUERY,(user_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        if not result:
            raise NoDataFoundError("User not found")
        return User(id=result[0], name=result[1], surname=result[2])
            

    def update(self, user: User) -> bool:
        """Update a user"""
        connection = DatabaseConnection().get_connection()
        cursor = connection.cursor()
        cursor.execute(UPDATE_USER_QUERY,(user.name, user.surname, user.id))
        connection.commit()
        cursor.close()
        connection.close()
        return True

    @classmethod
    def delete(cls, user_id: int) -> bool:
        """Delete a user by id"""
        connection = DatabaseConnection().get_connection()
        cursor = connection.cursor()
        cursor.execute(DELETE_USER_QUERY, (user_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return True
