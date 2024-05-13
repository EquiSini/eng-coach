from enum import Enum
from pydantic import BaseModel


class OauthService(Enum):
    GOOGLE = 'google'
    YANDEX = 'yandex'


class LoginRequest(BaseModel):
    code: str
    oauth_service: OauthService
