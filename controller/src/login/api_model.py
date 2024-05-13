from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel


class OauthService(Enum):
    GOOGLE = 'google'
    YANDEX = 'yandex'


class LoginRequest(BaseModel):
    code: str
    oauth_service: OauthService


@dataclass
class UserInfo:
    id: str
    display_name: str
    is_avatar_empty: bool
    expire: int
    default_avatar_url: str = None
    token: str = None
