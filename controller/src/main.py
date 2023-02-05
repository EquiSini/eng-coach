# Import the necessary modules
from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel
# Import the User model and the DatabaseConnection class
from .models import User, UserProducer, NoDataFoundError



class Message(BaseModel):
    message: str

# Define the app and the endpoints
app = FastAPI()

def custom_openapi():
    '''Swagger'''
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

