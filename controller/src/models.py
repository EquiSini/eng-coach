'''Model classes'''
import datetime
from pydantic import BaseModel
from .database import DatabaseConnection
import uuid

#CONSTS
INSERT_USER_QUERY = "INSERT INTO eng_user (username, email,auth_id, picture, session_token, session_expire) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"
SELECT_USER_QUERY = "SELECT id, username, email, auth_id, picture, session_token, session_expire FROM eng_user WHERE id = %s"
UPDATE_USER_QUERY = "UPDATE eng_user SET username=%s, email=%s, auth_id=%s, picture=%s, session_token=%s, session_expire=%s WHERE id=%s"
DELETE_USER_QUERY = "DELETE FROM eng_user WHERE id = %s"
GET_USER_ID_BY_AUTH_ID_QUERY = "SELECT id FROM eng_user WHERE auth_id = %s"
GET_USER_BY_SESSION_QUERY = "SELECT id, username, email, auth_id, picture, session_token, session_expire FROM eng_user WHERE session_token = %s"


class User(BaseModel):
    '''User dataclass'''
    id: int = 0
    username: str
    email: str
    auth_id: str
    picture: str
    session_token: str
    expire: datetime.datetime

    def expired(self):
        return self.expire < datetime.datetime.now()
    # pass: str pbkdf2 python

class IrregularVerb(BaseModel):
    '''Dataclass for irregular verbs'''
    id: int
    verb: str
    past: str
    past_participle: str
    verb_level: int

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

    @classmethod
    def create(cls, username:str, email:str,
            auth_id: str, picture: str,
            expire: datetime.datetime) -> User:
        """Create a new user"""
        session_token: str = str(uuid.uuid4())
        with DatabaseConnection() as db:
            cursor = db.connection.cursor()
            cursor.execute(INSERT_USER_QUERY, (username, email, auth_id, picture, session_token,expire.strftime('%Y-%m-%d %H:%M:%S.%f %Z')))
            result = cursor.fetchone()
            db.connection.commit()
            cursor.close()
            db.connection.close()
        return User(id=result[0], username=username, 
            email=email,
            auth_id=auth_id,
            picture=picture,
            session_token=session_token,
            expire=expire)

    @classmethod
    def get_by_id(cls, user_id:int) -> User:
        """Get a user by id"""
        with DatabaseConnection() as db:
            cursor = db.connection.cursor()
            cursor.execute(SELECT_USER_QUERY,(user_id,))
            result = cursor.fetchone()
            cursor.close()
            db.connection.close()
            if not result:
                raise NoDataFoundError("User not found")
        return User(id=result[0],
            username=result[1],
            email=result[2],
            auth_id=result[3],
            picture=result[4],
            session_token=result[5],
            expire=result[6])

    @classmethod
    def get_id_by_auth_id(cls, auth_id:str) -> int:
        """Get a user id by auth id. Returns -1 if not founded"""
        with DatabaseConnection() as db:
            cursor = db.connection.cursor()
            cursor.execute(GET_USER_ID_BY_AUTH_ID_QUERY,(auth_id,))
            result = cursor.fetchone()
            cursor.close()
            db.connection.close()
        if not result:
            return -1
        return result[0]

    @classmethod
    def get_by_session_token(cls, session_token:int) -> User:
        """Get a user info by session_token."""
        with DatabaseConnection() as db:
            cursor = db.connection.cursor()
            cursor.execute(GET_USER_BY_SESSION_QUERY,(session_token,))
            result = cursor.fetchone()
            cursor.close()
            db.connection.close()
        if not result:
            raise NoDataFoundError("User not found")
        return User(id=result[0],
            username=result[1],
            email=result[2],
            auth_id=result[3],
            picture=result[4],
            session_token=result[5],
            expire=result[6])


    @classmethod
    def update(cls, user: User) -> bool:
        """Update a user"""
        with DatabaseConnection() as db:
            cursor = db.connection.cursor()
            cursor.execute(UPDATE_USER_QUERY,(user.username,
                user.email,
                user.auth_id,
                user.picture,
                user.session_token,
                user.expire.strftime('%Y-%m-%d %H:%M:%S.%f %Z'),
                user.id))
            db.connection.commit()
            cursor.close()
            db.connection.close()
        return True

    @classmethod
    def delete(cls, user_id: int) -> bool:
        """Delete a user by id"""
        with DatabaseConnection() as db:
            cursor = db.connection.cursor()
            cursor.execute(DELETE_USER_QUERY, (user_id,))
            db.connection.commit()
            cursor.close()
            db.connection.close()
        return True
