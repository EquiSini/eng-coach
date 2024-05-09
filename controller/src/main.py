# Import the necessary modules
import os
import uuid
from typing import List
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel # pylint: disable=no-name-in-module
import uvicorn
from googleapiclient.discovery import build, HttpError, Resource
# import google.oauth2.credentials
import google_auth_oauthlib.flow

# Import the User model and the DatabaseConnection class
from .models import User, UserProducer, NoDataFoundError, VerbSelector, VerbChecker, UserScores
from .settings import CLIENT_SECRETS_JSON, SCOPES, FULL_HOST_NAME, PORT_NUMBER
from .settings import COOKIE_AUTHORIZATION_NAME, COOKIE_DOMAIN, AUTH_REDIRECT_URL_COOKIE
from .htmljs import HTML_HEAD, HTML_BODY, HTML_BODY_ROW


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
DATE_TIME_ZONE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
# Define the app and the endpoints
app = FastAPI()

#TODO split files and add routes https://fastapi.tiangolo.com/tutorial/bigger-applications/
#TODO add some pytests

@app.get("/google_login")
def authorize():
    '''Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.'''
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_JSON, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    #   flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    #TODO make universal url
    flow.redirect_uri = 'http://localhost/api/googleOauth2callback'#request.url_for('googleOauth2callback')#'http://localhost:8080'

    authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

    print("state:", state)
    return RedirectResponse(authorization_url)


async def get_user_info(credentials):
    '''Get user info and email using google oauth credentials'''
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        service: Resource
        user_info = service.userinfo().get().execute()
        return user_info
    except HttpError as error:
        raise HTTPException(
            status_code=error.resp.status, 
            detail=error._get_reason()) from error # pylint: disable=W0212

@app.get("/googleOauth2callback")
async def oauth2callback(request:Request, response: Response):
    '''Function for google oauth callback. If succseed redirect to previous point.'''
    print(request.cookies)
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_JSON,
        scopes=SCOPES)
    flow.redirect_uri = 'http://localhost/api/googleOauth2callback'

    authorization_response = request.url._url # pylint: disable=W0212
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session.
    credentials = flow.credentials

    user_info = await get_user_info(credentials)
    user_id = UserProducer().get_id_by_auth_id(user_info['id'])
    if user_id == -1:
        #New user
        user = UserProducer.create(
            username=user_info['name'],
            email=user_info['email'],
            auth_id=user_info['id'],
            picture=user_info['picture'],
            expire=credentials.expiry)
    else:
        user = UserProducer.get_by_id(user_id=user_id)
        user.username = user_info['name']
        user.email = user_info['email']
        user.auth_id = user_info['id']
        user.picture = user_info['picture']
        if user.session_token is None:
            user.session_token = str(uuid.uuid4())
        user.expire = credentials.expiry
        UserProducer.update(user)
    response = RedirectResponse(url="/")
    response.set_cookie(
        key=COOKIE_AUTHORIZATION_NAME,
        value=user.session_token,
        domain=COOKIE_DOMAIN)
    return response

@app.get("/frontendOauth2callback")
async def oauth2callback(request:Request, response: Response):
    '''require credentials'''
    print(request.cookies)
    # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        # 'src/client_secret_google.json',
        # scopes=SCOPES)
    # flow.redirect_uri = 'http://localhost/api/googleOauth2callback'
# 
    # authorization_response = request.url._url # pylint: disable=W0212
    # flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session.
    credentials = request.credentials

    user_info = await get_user_info(credentials)
    user_id = UserProducer().get_id_by_auth_id(user_info['id'])
    if user_id == -1:
        #New user
        user = UserProducer.create(
            username=user_info['name'],
            email=user_info['email'],
            auth_id=user_info['id'],
            picture=user_info['picture'],
            expire=credentials.expiry)
    else:
        user = UserProducer.get_by_id(user_id=user_id)
        user.username = user_info['name']
        user.email = user_info['email']
        user.auth_id = user_info['id']
        user.picture = user_info['picture']
        if user.session_token is None:
            user.session_token = str(uuid.uuid4())
        user.expire = credentials.expiry
        UserProducer.update(user)
    response = RedirectResponse(url="/")
    response.set_cookie(
        key=COOKIE_AUTHORIZATION_NAME,
        value=user.session_token,
        domain=COOKIE_DOMAIN)
    return response

def authentificate(request: Request) -> User:
    """Authentificate user. Return -1 if user not founded or he haven't cookie"""
    if not COOKIE_AUTHORIZATION_NAME in request.cookies:
        return UserProducer().get_no_user()
    try:
        user = UserProducer().get_by_session_token(request.cookies[COOKIE_AUTHORIZATION_NAME])
        if user.expired():
            return UserProducer().get_no_user()
        return user
    except NoDataFoundError:
        return UserProducer().get_no_user()

def make_auth_redirect_response(request: Request) -> RedirectResponse:
    '''Stores in cookies current url and makes redirect response'''
    response = RedirectResponse('google_login')
    response.set_cookie(key=AUTH_REDIRECT_URL_COOKIE,
        value=request.url._url, domain=COOKIE_DOMAIN) # pylint: disable=W0212
    return response

#TODO add revoke
# @app.get('/revoke') To add revoke need to store credentials in base
# def revoke():
#   if 'credentials' not in flask.session:
#     return ('You need to <a href="/authorize">authorize</a> before ' +
#             'testing the code to revoke credentials.')

#   credentials = google.oauth2.credentials.Credentials(
#     **flask.session['credentials'])

#   revoke = requests.post('https://oauth2.googleapis.com/revoke',
#       params={'token': credentials.token},
#       headers = {'content-type': 'application/x-www-form-urlencoded'})

#   status_code = getattr(revoke, 'status_code')
#   if status_code == 200:
#     return('Credentials successfully revoked.' + print_index_table())
#   else:
#     return('An error occurred.' + print_index_table())

# Pages:

# @app.get("/")
# async def homepage():
#     '''Some homepage stub'''
#     return 


@app.get("/test")
async def homeapi():
    '''Some homepage stub'''
    return {"ping-pong": True}

def make_task_html_page(count:int = 5):
    '''Generator html page for makeTask'''
    body = HTML_BODY.format(
        table_body=''.join([HTML_BODY_ROW.format(ind=ind) for ind in range(count)]))
    return f'{HTML_HEAD}{body}'

@app.get("/makeTask")
async def make_task(request: Request):
    '''Generate page for makeTask'''
    if  authentificate(request).id == -1:
        return make_auth_redirect_response(request)
    return HTMLResponse(make_task_html_page(), status_code=200)

class Message(BaseModel): #pylint: disable=R0903
    '''Message class'''
    message: str

class Answer(BaseModel): #pylint: disable=R0903
    '''Answer class'''
    id: int
    answer1: str
    answer2: str

def custom_openapi():
    '''OpenAPI'''
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom title",
        version="2.5.0",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# @app.get("/users/{user_id}", response_model=User, responses={404: {"model": Message}})
# async def read_user(request: Request, request_user_id: int) -> User:
#     """Get a user by id"""
#     if authentificate(request).id == -1:
#         return make_auth_redirect_response(request)
#     return UserProducer().get_by_id(request_user_id)

@app.get("/profile", response_model=User, responses={404: {"model": Message}})
async def user_profile(request: Request) -> User:
    """Get a current user by session"""
    user = authentificate(request)
    if  user.id == -1:
        return make_auth_redirect_response(request)
    return user


@app.get("/scores")
async def get_scores(request: Request):
    '''Return JSON with user irregular_verb scores'''
    user = authentificate(request)
    if  user.id == -1:
        return make_auth_redirect_response(request)
    return UserScores(user.id).getScores()

@app.get("/example")
async def get_example(request: Request) -> list:
    '''Randomly based on user verb scores makes example. Returns list of IrregulaVerb'''
    user = authentificate(request)
    if user.id == -1:
        return make_auth_redirect_response(request)
    return VerbSelector(5, user.id, 2).generate_list()


@app.post("/example/submit")
async def submit_answer(request: Request, answers: List[Answer]):
    '''Checks user answer. Returns mistakes and scores lists.'''
    user = authentificate(request)
    if  user.id == -1:
        return make_auth_redirect_response(request)
    vc = VerbChecker(user.id)
    fails = []
    scores = []
    for ind,ans in enumerate(answers):
        success, score = vc.check_Verb(ans.id, ans.answer1, ans.answer2)
        scores.append(score)
        if not success:
            fails.append(ind)
    return {"message": "Answers submitted successfully",
        "mistakes": fails,
        "scores":scores}



def main():
    '''Main function'''
    uvicorn.run(app, host=FULL_HOST_NAME, port=PORT_NUMBER)

if __name__ == "__main__":
    main()
