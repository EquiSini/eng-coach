'''Model classes'''
import datetime
import uuid
import numpy as np
from pydantic import BaseModel # pylint: disable=no-name-in-module
from .database import DatabaseConnection


#CONSTS
INSERT_USER_QUERY = "INSERT INTO eng_user (username, email,auth_id, picture, session_token, session_expire) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"
SELECT_USER_QUERY = "SELECT id, username, email, auth_id, picture, session_token, session_expire FROM eng_user WHERE id = %s"
UPDATE_USER_QUERY = "UPDATE eng_user SET username=%s, email=%s, auth_id=%s, picture=%s, session_token=%s, session_expire=%s WHERE id=%s"
DELETE_USER_QUERY = "DELETE FROM eng_user WHERE id = %s"
GET_USER_ID_BY_AUTH_ID_QUERY = "SELECT id FROM eng_user WHERE auth_id = %s"
GET_USER_BY_SESSION_QUERY = "SELECT id, username, email, auth_id, picture, session_token, session_expire FROM eng_user WHERE session_token = %s"
GET_USER_VERBS_SCORE = """select iv.id as verb_id, ivus.score from irregular_verbs iv 
left outer join irregular_verbs_user_score ivus on iv.id=ivus.verb_id and ivus.user_id = %s
where verb_level <= %s"""
GET_USER_VERB_SCORE_FOR_CHECK = """select iv.id as verb_id,
iv.verb, 
iv.past, 
iv.past_participle, 
ivus.score 
from irregular_verbs iv 
left outer join irregular_verbs_user_score ivus on iv.id=ivus.verb_id and ivus.user_id = %s
where iv.id = %s"""
GET_USER_VERB_SCORES = """select iv.verb, 
ivus.score 
from irregular_verbs iv 
left outer join irregular_verbs_user_score ivus on iv.id=ivus.verb_id and ivus.user_id = %s
ORDER BY case when ivus.score is null then 1 else 0 end, ivus.score DESC"""
UPDATE_USER_VERB_SCORE = '''
INSERT INTO irregular_verbs_user_score (user_id, verb_id, score) 
VALUES (%s, %s, %s)
ON CONFLICT (user_id, verb_id) DO UPDATE 
SET score=%s'''
GET_IRREGULAR_VERB = """SELECT id, verb, past, past_participle, verb_level
FROM irregular_verbs
WHERE id = %s"""



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
    score: float

class NoDataFoundError(Exception):
    '''Class for no data errors'''
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class UserScores:
    '''User scores for irregular verbs'''
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def getScores(self):
        verbs = {}
        with DatabaseConnection() as db:
            cursor = db.connection.cursor()
            cursor.execute(GET_USER_VERB_SCORES,(
                self.user_id,))
            results = cursor.fetchall()
            for result in results:
                verbs[result[0]] = 0.5 if result[1] is None else result[1]
        return verbs

class VerbSelector:
    '''Selector irregular verbs for user'''

    def __init__(self, verbs_count: int, user_id: int, level: int) -> None:
        self.verbs_count = verbs_count
        self.user_id = user_id
        self.level = level

    def generate_list(self):
        '''Generate list of irregular vervs'''
        #TODO add cacheing
        with DatabaseConnection() as db:
            cursor = db.connection.cursor()
            cursor.execute(GET_USER_VERBS_SCORE,(
                self.user_id,
                self.level))
            results = cursor.fetchall()
            ids = list()
            scores = list()
            probs = list()
            for verb_id, score in results:
                prob = float(1-score) if score is not None else 0.5
                ids.append(verb_id)
                scores.append(prob**2)
                probs.append(1-prob)
            scores_norm = scores / np.sum(scores)
            cursor.close()
            db.connection.close()
        verbs = list()
        with DatabaseConnection() as db:
            for ind in np.random.choice([i for i in range(len(ids))], 
                                        size=self.verbs_count, 
                                        replace=False, 
                                        p=scores_norm):
                cursor = db.connection.cursor()
                cursor.execute(GET_IRREGULAR_VERB,(int(ids[ind]),))
                result = cursor.fetchone()
                verbs.append(IrregularVerb(
                    id=result[0],
                    verb=result[1],
                    past=result[2],
                    past_participle=result[3],
                    verb_level = result[4],
                    score=probs[ind]).dict())
                cursor.close()
            db.connection.close()
        return verbs

class VerbChecker():
    '''Check irregular verb and change score'''
    def __init__(self, user_id) -> None:
        self.user_id = user_id

    def check_Verb(self, verb_id, past, past_participle):
        rez = False
        rez_score = 0.5
        with DatabaseConnection() as db:
            cursor = db.connection.cursor()
            cursor.execute(GET_USER_VERB_SCORE_FOR_CHECK,(
                self.user_id,
                verb_id))
            result = cursor.fetchone()
            score = float(result[4]) if result[4] is not None else 0.5
            if (result[2].strip().upper() == past.strip().upper() 
                and result[3].strip().upper() == past_participle.strip().upper()):
                rez = True
            cursor.close()
            cursor = db.connection.cursor()
            rez_score = score+(1-score)/4 if rez else score-score/2
            cursor.execute(UPDATE_USER_VERB_SCORE,(
                self.user_id,
                verb_id,
                rez_score,
                rez_score))
            db.connection.commit()
            cursor.close()
            db.connection.close()
        return rez, rez_score

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
    def get_no_user(cls) -> User:
        '''Generator no user'''
        return User(id = -1,
            username='NO_USER',
            email='NO_USER',
            picture='NO_USER',
            auth_id='NO_USER',
            session_token='NO_USER',
            expire=datetime.datetime.now())


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
