from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class OauthService(Enum):
    GOOGLE = 'google'
    YANDEX = 'yandex'


class LoginRequest(BaseModel):
    """
Represents a login request.

Attributes:
- code (str): The login code.
- oauth_service (OauthService): The OAuth service used for authentication.
    """
    code: str
    oauth_service: OauthService


class UserInfo(BaseModel):
    """
Represents user information.

Attributes:
- id (int): The user's ID.
- display_name (str): The user's display name.
- is_avatar_empty (bool): Indicates if the user's avatar is empty.
- expire (int): The expiration time of the user's information.
- default_avatar_url (str, optional): The default avatar URL. Defaults to None.
- token (str, optional): The user's token. Defaults to None.
    """
    id: int
    display_name: str
    is_avatar_empty: bool
    expire: int
    default_avatar_url: str = None
    token: Optional[str] = None


class JwtInfo(BaseModel):
    token: str
    user_auth_id: str


class Message(BaseModel):
    '''Message class'''
    message: str


class Answer(BaseModel):
    '''Answer class
    Args:
        - id (int): The id of the verb being answered.
        - answer1 (str): Past Simple form.
        - answer2 (str): Past Participle form.
    '''
    id: int
    answer1: str
    answer2: str


class submitAnswerResponse(BaseModel):
    '''
submitAnswer response class
Args:
- message (str): A success message indicating that the answers were
submitted successfully.
- mistakes (List[int]): A list of indices indicating the positions of
incorrect answers.
- scores (List[float]): A list of scores corresponding to each answer.
    '''
    message: str
    mistakes: List[int]
    scores: List[float]


class ExampleResponseElement(BaseModel):
    """
Represents a verb object.

Attributes:
- id (int): The ID of the verb.
- verb (str): The base form of the verb.
- past (str): The past simple form of the verb.
- past_participle (str): The past participle form of the verb.
- verb_level (int): The level of the verb.
- score (float): The score of the verb.
    """
    id: int
    verb: str
    past: str
    past_participle: str
    verb_level: int
    score: float
