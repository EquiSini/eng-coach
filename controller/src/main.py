# Import the necessary modules
import os
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel, parse_obj_as
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Depends, Request, Response, HTTPException
import uuid
from starlette.middleware.sessions import SessionMiddleware
from googleapiclient.discovery import build, HttpError
import datetime
import google.oauth2.credentials
import google_auth_oauthlib.flow
from typing import List

# Import the User model and the DatabaseConnection class
from .models import User, UserProducer, NoDataFoundError
from .settings import CLIENT_SECRETS_JSON, SCOPES, API_SERVICE_NAME, API_VERSION, API_LOCATION
from .settings import COOKIE_AUTHORIZATION_NAME, COOKIE_DOMAIN


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
DATE_TIME_ZONE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
# Define the app and the endpoints
app = FastAPI()

# app.add_middleware(SessionMiddleware, secret_key="some-random-string")

# @app.middleware("http")
# async def some_middleware(request: Request, call_next):
#     response = await call_next(request)
#     session = request.cookies.get('session')
#     if session:
#         response.set_cookie(key='session', value=request.cookies.get('session'), httponly=True)
#     return response

@app.get("/google_login")
def authorize(request: Request):
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_JSON, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
#   flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    flow.redirect_uri = 'http://localhost:8080/googleOauth2callback'#request.url_for('googleOauth2callback')#'http://localhost:8080'

    authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

    print("state:", state)
  # Store the state so the callback can verify the auth server response.
    # app.session['state'] = state

    return RedirectResponse(authorization_url)


async def get_user_info(credentials):
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info
    except HttpError as error:
        raise HTTPException(status_code=error.resp.status, detail=error._get_reason())

@app.get("/googleOauth2callback")
async def oauth2callback(request:Request, response: Response):
    # state = request.cookies["state"]
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'src/client_secret_google.json',
        scopes=SCOPES) #,
        #state=state)
    flow.redirect_uri = 'http://localhost:8080/googleOauth2callback' #response.url_for('oauth2callback', _external=True)

    authorization_response = request.url._url
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
        user.session_token = str(uuid.uuid4())
        user.expire = credentials.expiry
        UserProducer.update(user)
    response = RedirectResponse(url="/")
    response.set_cookie(key=COOKIE_AUTHORIZATION_NAME,
        value=user.session_token,
        domain=COOKIE_DOMAIN)
    return response

def check_cookie(cookies: str) -> bool:
    '''Check for session cookie'''
    if COOKIE_AUTHORIZATION_NAME in cookies:
        return True
    return False

#TODO add revoke method
# @app.get('/revoke')
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

class Message(BaseModel):
    message: str

@app.get("/")
async def homepage():
    return "Welcome to eng coach!"

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

@app.get("/users/{user_id}", response_model=User, responses={404: {"model": Message}})
async def read_user(request: Request, user_id: int) -> User:
    """Get a user by id"""
    if not check_cookie(request.cookies):
        return RedirectResponse('google_login')
    try:
        user = UserProducer().get_by_id(user_id)
        return user
    except NoDataFoundError:
        return RedirectResponse('google_login')

@app.get("/profile", response_model=User, responses={404: {"model": Message}})
async def user_profile(request: Request) -> User:
    """Get a user by id"""
    if not check_cookie(request.cookies):
        return RedirectResponse('google_login')
    try:
        user = UserProducer().get_by_session_token(request.cookies[COOKIE_AUTHORIZATION_NAME])
        if user.expired():
            return RedirectResponse('google_login')
        return user
    except NoDataFoundError:
        return RedirectResponse('google_login')

def make_task_html_page():
    head = '''<!DOCTYPE html>
<html>
  <head>
    <script>
        let ids = [];

      function getExampleValues() {
        // Fetch the example values from the /getExample endpoint
        fetch("/getExample")
          .then(response => response.json())
          .then(data => {
            // Populate the first column of edit fields with the values from the response
            ids = [];
            for (let i = 0; i < 5; i++) {
                ids.push(data[i].id);
                document.getElementById(`example_${i}`).value = data[i].word;
            }
          });
      }

      async function submitForm() {
        // Collect the answers from the form
        let answers = [];
        for (let i = 0; i < 5; i++) {
          let answer1 = document.getElementById("answer1_" + i).value;
          let answer2 = document.getElementById("answer2_" + i).value;
          let id = ids[i];
          answers.push({ id, answer1, answer2 });
        }

        // Send the answers to the API
        let response = await fetch("/submitAnswer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(answers),
        });
        let data = await response.json();

        // Check the response for errors
        if (data.mistakes.length > 0) {
          for (let i = 0; i < data.mistakes.length; i++) {
            document.getElementById("row_" + data.mistakes[i]).style.backgroundColor = "red";
          }
        } else {
          location.reload();
        }
      }
    </script>
  </head>
'''
    body = '''  <body onload="getExampleValues()">
    <form>
      <table>
        <tbody>
          {table_body}
        </tbody>
      </table>
      <button type="button" onclick="submitForm()">Submit</button>
    </form>
  </body>
</html>'''
    row = '''<tr id="row_{ind}">
              <td>
                <input type="text" id="example_{ind}" disabled>
              </td>
              <td>
                <input type="text" id="answer1_{ind}">
              </td>
              <td>
                <input type="text" id="answer2_{ind}">
              </td>
            </tr>
            '''
    return '{}{}'.format(
        head,
        body.format(table_body=''.join([row.format(ind=ind) for ind in range(5)]))
    )

@app.get("/makeTask")
async def make_task(request: Request):
    if not check_cookie(request.cookies):
        return RedirectResponse('google_login')
    try:
        user = UserProducer().get_by_session_token(request.cookies[COOKIE_AUTHORIZATION_NAME])
        if user.expired():
            return RedirectResponse('google_login')
        return HTMLResponse(make_task_html_page(), status_code=200)
    except NoDataFoundError:
        return RedirectResponse('google_login')

@app.get("/getExample")
async def getExample(request: Request) -> list:
    if not check_cookie(request.cookies):
        return RedirectResponse('google_login')
    try:
        user = UserProducer().get_by_session_token(request.cookies[COOKIE_AUTHORIZATION_NAME])
        if user.expired():
            return RedirectResponse('google_login')
        return [
    {
      "id": 100,
      "word": "be"
    },
    {
      "id": 101,
      "word": "fall"
    },
    {
      "id": 102,
      "word": "loose"
    },
    {
      "id": 103,
      "word": "stand"
    },
    {
      "id": 104,
      "word": "buy"
    }]
    except NoDataFoundError:
        return RedirectResponse('google_login')

class Answer(BaseModel):
    id: int
    answer1: str
    answer2: str

@app.post("/submitAnswer")
async def submit_answer(request: Request, answers: List[Answer]):
    if not check_cookie(request.cookies):
        return RedirectResponse('google_login')
    try:
        user = UserProducer().get_by_session_token(request.cookies[COOKIE_AUTHORIZATION_NAME])
        if user.expired():
            return RedirectResponse('google_login')
        print(answers)
        return {"message": "Answers submitted successfully",
            "mistakes": [2, 4]}
    except NoDataFoundError:
        return RedirectResponse('google_login')
