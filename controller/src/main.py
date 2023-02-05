# Import the necessary modules
import os
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from typing import Optional
from datetime import datetime, timedelta

import jwt
from jwt import PyJWTError

from fastapi import Depends, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security.oauth2 import (
    OAuth2,
    OAuthFlowsModel,
    get_authorization_scheme_param,
)
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse
from starlette.requests import Request

from pydantic import BaseModel

import httplib2
from oauth2client import client
from google.oauth2 import id_token
from google.auth.transport import requests

# Import the User model and the DatabaseConnection class
from .models import User, UserProducer, NoDataFoundError
from .settings import SECRET_KEY, ALGORITHM, SWAP_TOKEN_ENDPOINT, CLIENT_SECRETS_JSON, CLIENT_ID
from .settings import ACCESS_TOKEN_EXPIRE_MINUTES, COOKIE_AUTHORIZATION_NAME, COOKIE_DOMAIN, ERROR_ROUTE
from .htmljs import google_login_javascript_client,google_login_javascript_server

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None
    email: str = None

class Message(BaseModel):
    message: str

class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/token")
# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
# Define the app and the endpoints
app = FastAPI()

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "myemail@gmail.com",
        "disabled": False,
    }
}

def get_user_by_email(db, email: str):
    for username, value in db.items():
        if value.get("email") == email:
            user_dict = db[username]
            return User(**user_dict)


def authenticate_user_email(fake_db, email: str):
    user = get_user_by_email(fake_db, email)
    if not user:
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except PyJWTError:
        raise credentials_exception
    user = get_user_by_email(fake_users_db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/google_login_client", tags=["security"])
def google_login_client():

    return HTMLResponse(google_login_javascript_client)


@app.get("/google_login_server", tags=["security"])
def google_login_server():

    return HTMLResponse(google_login_javascript_server)


@app.post(f"{SWAP_TOKEN_ENDPOINT}", response_model=Token, tags=["security"])
async def swap_token(request: Request = None):
    if not request.headers.get("X-Requested-With"):
        raise HTTPException(status_code=400, detail="Incorrect headers")

    google_client_type = request.headers.get("X-Google-OAuth2-Type")

    if google_client_type == 'server':
        try:
            body_bytes = await request.body()
            auth_code = jsonable_encoder(body_bytes)

            credentials = client.credentials_from_clientsecrets_and_code(
                CLIENT_SECRETS_JSON, ["profile", "email"], auth_code
            )

            http_auth = credentials.authorize(httplib2.Http())

            email = credentials.id_token["email"]

        except:
            raise HTTPException(status_code=400, detail="Unable to validate social login")


    if google_client_type == 'client':
        body_bytes = await request.body()
        auth_code = jsonable_encoder(body_bytes)

        try:
            idinfo = id_token.verify_oauth2_token(auth_code, requests.Request(), CLIENT_ID)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            if idinfo['email'] and idinfo['email_verified']:
                email = idinfo.get('email')

            else:
                raise HTTPException(status_code=400, detail="Unable to validate social login")

        except:
            raise HTTPException(status_code=400, detail="Unable to validate social login")

    authenticated_user = authenticate_user_email(fake_users_db, email)

    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Incorrect email address")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": authenticated_user.email}, expires_delta=access_token_expires
    )

    token = jsonable_encoder(access_token)

    response = JSONResponse({"access_token": token, "token_type": "bearer"})

    response.set_cookie(
        COOKIE_AUTHORIZATION_NAME,
        value=f"Bearer {token}",
        domain=COOKIE_DOMAIN,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response


@app.get("/")
async def homepage():
    return "Welcome to the security test!"


@app.get(f"{ERROR_ROUTE}", tags=["security"])
async def login_error():
    return "Something went wrong logging in!"


@app.get("/logout", tags=["security"])
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/")
    response.delete_cookie(COOKIE_AUTHORIZATION_NAME, domain=COOKIE_DOMAIN)
    return response


@app.get("/openapi.json", tags=["documentation"])
async def get_open_api_endpoint(current_user: User = Depends(get_current_active_user)):
    response = JSONResponse(
        get_openapi(title="FastAPI security test", version=1, routes=app.routes)
    )
    return response


@app.get("/documentation", tags=["documentation"])
async def get_documentation(current_user: User = Depends(get_current_active_user)):
    response = get_swagger_ui_html(openapi_url="/openapi.json", title="docs")
    return response


@app.get("/secure_endpoint", tags=["security"])
async def get_open_api_endpoint(current_user: User = Depends(get_current_active_user)):
    response = "How cool is this?"
    return response


@app.get("/users/me/", response_model=User, tags=["users"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/", tags=["users"])
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]




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

@app.post("/users")
async def create_user(name: str, surname: str) -> User:
    """Create a new user"""
    return UserProducer().create(name, surname)

@app.get("/users/{user_id}", response_model=User, responses={404: {"model": Message}})
async def read_user(user_id: int) -> User:
    """Get a user by id"""
    try:
        user = UserProducer().read(user_id)
        return user
    except NoDataFoundError as err:
        return JSONResponse(status_code=404, content={"message": err.message})


@app.put("/users/{user_id}")
async def update_user(user: User) -> bool:
    """Update a user"""
    return UserProducer().update(user)

@app.delete("/users/{user_id}")
async def delete_user(user_id: int) -> bool:
    """Delete a user by id"""
    return UserProducer().delete(user_id)

