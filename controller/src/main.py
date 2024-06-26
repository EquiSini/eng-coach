# Import the necessary modules
import datetime
import os
from typing import List, Optional

from fastapi import Depends, FastAPI, Request, HTTPException, status
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer

from .logger import LOGGER
import uvicorn  # type: ignore
import jwt  # type: ignore


# Import the User model and the DatabaseConnection class
from .models import (
    User,
    UserProducer,
    VerbSelector,
    VerbChecker,
    UserScores)
from .settings import (
    JWT_SECRET,
    FULL_HOST_NAME,
    PORT_NUMBER)
from .login.api_model import (
    Answer,
    ExampleResponseElement,
    JwtInfo,
    LoginRequest,
    OauthService,
    UserInfo,
    submitAnswerResponse)
from .login.oauth import YandexOauthGetter


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
DATE_TIME_ZONE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class JwtHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        from fastapi import status
        try:
            r = await super().__call__(request)
            token = r.credentials
            payload = jwt.decode(token, JWT_SECRET, algorithms='HS256')
            auth_user_id: str = payload.get("id")
            if auth_user_id is None:
                raise ValueError('No id in jwt-token')
        except HTTPException as ex:
            assert ex.status_code == status.HTTP_403_FORBIDDEN, ex
            auth_user_id = None
        return JwtInfo(
            token=token,
            user_auth_id=auth_user_id)


def custom_openapi():
    '''OpenAPI'''
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Eng-coach",
        version="1.0.0",
        description="OpenAPI schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


oauth2_scheme = JwtHTTPBearer(auto_error=True)


# TODO debug as env for prod
app = FastAPI(debug=True)
app.openapi = custom_openapi


# TODO split files and add routes
# https://fastapi.tiangolo.com/tutorial/bigger-applications/
# TODO add some pytests
@app.post("/login")
async def login(request: LoginRequest) -> UserInfo:
    """
Handle user login and return user information.

Args:
* code (str): The login code.
* oauth_service (OauthService): The OAuth service used for
authentication. Accept 'google' or 'yandex'

Returns:
- id (str): The user's ID.
- display_name (str): The user's display name.
- is_avatar_empty (bool): Indicates if the user's avatar is empty.
- expire (int): The expiration time of the user's information.
- default_avatar_url (str, optional): The default avatar URL. Defaults to None.
- token (str, optional): The user's token. Defaults to None.
    """
    if request.oauth_service is OauthService.YANDEX:
        yog = YandexOauthGetter(request.code)
        oauth_user = yog.get_user_info()
        local_user_id = UserProducer().get_id_by_auth_id(oauth_user.id)
        if local_user_id == -1:
            # New user
            # TODO УБРАТЬ СОХРАНЕНИЕ ПОЧТЫ И ИМЕНИ И АВАТАРКИ
            user = UserProducer.create(
                username=oauth_user.display_name,
                auth_id=oauth_user.id,
                picture=oauth_user.default_avatar_url,
                expire=datetime.datetime.fromtimestamp(oauth_user.expire))
        else:
            user = UserProducer.get_by_id(local_user_id)
        return UserInfo(
            id=user.id,
            display_name=user.username,
            is_avatar_empty=user.picture == '',
            default_avatar_url=user.picture,
            expire=int(user.expire.timestamp()),
            token=oauth_user.token
        )
    # Store the credentials in the session.
    # TODO add google oauth
    return UserInfo(
            id=-1,
            display_name='Ivan Pupkin',
            is_avatar_empty=True,
            default_avatar_url='avatar_url',
            token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImdfMDAwMSIsImV4dCI6MTc0Njk2NTc4NX0.yFTWh7X1EdhaV2y9mRhfdQ9Ye10jFQ_HXycd26U2gHE',  # noqa: E501
            expire=1746965785
        )


def authentificate(user_auth_id: str) -> User:
    """
Authentificate user.

This function takes a user authentication ID as input and returns the
corresponding User object.

Parameters:
- user_auth_id (str): The authentication ID of the user.

Returns:
- User: The User object corresponding to the authentication ID
    """
    user_id = UserProducer.get_id_by_auth_id(user_auth_id)
    return UserProducer.get_by_id(user_id)

# TODO add revoke
# @app.get('/revoke') To add revoke need to store credentials in base
# def revoke():
#    pass


@app.get("/user")
async def get_user(auth_data: JwtInfo = Depends(oauth2_scheme)) -> UserInfo:
    '''
Retrieve user information.
Requires user authentication.

Returns:
- id (int): The user's ID.
- username (str): The user's username.
- picture (str): URL to the user's profile picture.
- expire (datetime.datetime): The expiration date of the user's session.

Raises:
- HTTPException: If the credentials cannot be validated.
    '''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = authentificate(auth_data.user_auth_id)
        return UserInfo(
            id=user.id,
            display_name=user.username,
            is_avatar_empty=user.picture == '',
            default_avatar_url=user.picture,
            expire=int(user.expire.timestamp()),
            token=auth_data.token
        )
    except Exception as e:
        LOGGER.error(e)
        raise credentials_exception


@app.get("/scores")
async def get_scores(auth_data: JwtInfo = Depends(oauth2_scheme)) -> dict:
    '''
Return JSON with user irregular_verb scores
Requires user authentication.

Returns:
- dict: A dictionary containing the user's irregular verb scores:
    - key: verb id
    - value: score
    '''
    user = authentificate(auth_data.user_auth_id)
    return UserScores(user.id).getScores()


@app.get("/example")
async def get_example(
        auth_data: JwtInfo = Depends(oauth2_scheme)
        ) -> list[ExampleResponseElement]:
    '''
Randomly generates an example based on the user's verb scores.
Requires user authentication.

Returns:
- list: A list of IrregularVerb objects representing the generated
example. For each:
    - id (int): The ID of the verb.
    - verb (str): The base form of the verb.
    - past (str): The past simple form of the verb.
    - past_participle (str): The past participle form of the verb.
    - verb_level (int): The level of the verb.
    - score (float): Current user score of the verb.
    '''
    user = authentificate(auth_data.user_auth_id)
    return VerbSelector(5, user.id, 2).generate_list()


@app.post("/example/submit")
async def submit_answer(
        answers: List[Answer],
        auth_data: JwtInfo = Depends(oauth2_scheme)) -> submitAnswerResponse:
    '''
Checks user answer. Returns mistakes and scores lists.
Requires user authentication.

Args:
- List of Answer objects containing user's answers:
    - id (int): The id of the verb being answered.
    - answer1 (str): Past Simple form.
    - answer2 (str): Past Participle form.

Returns:
- "message": A success message indicating that the answers were submitted
successfully.
- "mistakes": A list of indices indicating the positions of incorrect
answers.
- "scores": A list of scores corresponding to each answer.
    '''
    user = authentificate(auth_data.user_auth_id)
    vc = VerbChecker(user.id)
    fails = []
    scores = []
    for ind, ans in enumerate(answers):
        success, score = vc.check_Verb(ans.id, ans.answer1, ans.answer2)
        scores.append(score)
        if not success:
            fails.append(ind)
    return submitAnswerResponse(
        message="Answers submitted successfully",
        mistakes=fails,
        scores=scores
    )


def main():
    '''Main function'''
    uvicorn.run(app, host=FULL_HOST_NAME, port=PORT_NUMBER)


if __name__ == "__main__":
    main()
