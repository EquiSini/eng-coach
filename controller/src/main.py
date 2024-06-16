# Import the necessary modules
import datetime
import os
from typing import List, Optional

from fastapi import Depends, FastAPI, Request, HTTPException, status
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer

import uvicorn  # type: ignore
import jwt  # type: ignore
import logging
import sys

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
    LoginRequest,
    OauthService,
    UserInfo,
    submitAnswerResponse)
from .login.oauth import YandexOauthGetter


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
DATE_TIME_ZONE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def setup_custom_logger(name):
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('controller/controller.log', mode='a')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger


LOGGER = setup_custom_logger('Controller')


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
        return auth_user_id


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
    '''Handle user login and return user information.'''
    if request.oauth_service is OauthService.YANDEX:
        yog = YandexOauthGetter(request.code)
        user = yog.get_user_info()
        local_user_id = UserProducer().get_id_by_auth_id(user.id)
        print(local_user_id)
        if local_user_id == -1:
            # New user
            # TODO УБРАТЬ СОХРАНЕНИЕ ПОЧТЫ И ИМЕНИ И АВАТАРКИ
            UserProducer.create(
                username=user.display_name,
                email='email',
                auth_id=user.id,
                picture=user.default_avatar_url,
                expire=datetime.datetime.fromtimestamp(user.expire))
        return user
    # Store the credentials in the session.
    # TODO add google oauth
    return UserInfo(
            id='g_0001',
            display_name='Ivan Pupkin',
            is_avatar_empty=True,
            default_avatar_url='avatar_url',
            token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImdfMDAwMSIsImV4dCI6MTc0Njk2NTc4NX0.yFTWh7X1EdhaV2y9mRhfdQ9Ye10jFQ_HXycd26U2gHE',  # noqa: E501
            expire=1746965785
        )


def authentificate(user_auth_id: str) -> User:
    """Authentificate user. Return -1 if user not founded"""
    user_id = UserProducer.get_id_by_auth_id(user_auth_id)
    return UserProducer.get_by_id(user_id)

# TODO add revoke
# @app.get('/revoke') To add revoke need to store credentials in base
# def revoke():
#    pass


@app.get("/user")
async def get_user(user_auth_id: str = Depends(oauth2_scheme)) -> User:
    '''
    Retrieve user information.
    Requires user authentication.

    Returns:
    - User: The user object containing the user information.

    Raises:
    - HTTPException: If the credentials cannot be validated.
    '''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        return authentificate(user_auth_id)
    except Exception as e:
        print(e)
        raise credentials_exception


@app.get("/scores")
async def get_scores(user_auth_id: str = Depends(oauth2_scheme)) -> dict:
    '''
    Return JSON with user irregular_verb scores
    Requires user authentication.

    Returns:
        dict: A dictionary containing the user's irregular verb scores:
            key: verb id
            value: score
    '''
    user = authentificate(user_auth_id)
    return UserScores(user.id).getScores()


@app.get("/example")
async def get_example(
        user_auth_id: str = Depends(oauth2_scheme)
        ) -> list[ExampleResponseElement]:
    '''Randomly generates an example based on the user's verb scores.
    Requires user authentication.

    Returns:
        list: A list of IrregularVerb objects representing the generated
            example. For each:
                id (int): The ID of the verb.
                verb (str): The base form of the verb.
                past (str): The past simple form of the verb.
                past_participle (str): The past participle form of the verb.
                verb_level (int): The level of the verb.
                score (float): The score of the verb.
    '''
    user = authentificate(user_auth_id)
    return VerbSelector(5, user.id, 2).generate_list()


@app.post("/example/submit")
async def submit_answer(
        answers: List[Answer],
        user_auth_id: str = Depends(oauth2_scheme)) -> submitAnswerResponse:
    '''Checks user answer. Returns mistakes and scores lists.
    Requires user authentication.

    Args:
        answers (List[Answer]): A list of Answer objects containing user's
            answers:
                id (int): The id of the verb being answered.
                answer1 (str): Past Simple form.
                answer2 (str): Past Participle form.

    Returns:
        dict: A dictionary containing the following keys:
            - "message": A success message indicating that the answers were
                submitted successfully.
            - "mistakes": A list of indices indicating the positions of
                incorrect answers.
            - "scores": A list of scores corresponding to each answer.

    '''
    user = authentificate(user_auth_id)
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
