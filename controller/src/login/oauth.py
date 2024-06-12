from abc import ABC, abstractmethod
import datetime
import requests
import jwt  # type: ignore

from .api_model import UserInfo
from ..settings import JWT_SECRET, YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET

GOOGLE_TOKEN_EXCHANGE_URL = 'https://oauth2.googleapis.com/token'
YANDEX_TOKEN_EXCHANGE_URL = 'https://oauth.yandex.ru/token'
YANDEX_USERINFO_API_URL = 'https://login.yandex.ru/info?format=json'
OAUTH_AUTH_HEADER_TEMPLATE = 'OAuth {token}'
AVATAR_SIZE_CODE = 'islands-retina-50'
AVATAR_URL_TEMPLATE = 'https://avatars.yandex.net/get-yapic/{avatar_id}/{size}'


class OauthGetterBase(ABC):
    def __init__(
            self,
            code: str) -> None:
        super().__init__()
        self.code = code
        self.exchange_url = ''
        self.client_id = ''
        self.client_secret = ''

    @abstractmethod
    def _exchange_code_for_token(self) -> None:
        pass

    @abstractmethod
    def _get_user_info_by_token(self) -> UserInfo:
        pass

    def get_user_info(self) -> UserInfo:
        self._exchange_code_for_token()
        return self._get_user_info_by_token()


class GoogleOauthGetter(OauthGetterBase):
    def __init__(
            self,
            code: str) -> None:
        super().__init__(code)
        self.code = code
        self.exchange_url = GOOGLE_TOKEN_EXCHANGE_URL


class YandexOauthGetter(OauthGetterBase):
    # TODO бработка ошибки от яндекса
    def _exchange_code_for_token(self):
        session = requests.Session()
        session.auth = (YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        params = {
            "grant_type": 'authorization_code',
            'code': self.code
        }

        response = session.post(
            YANDEX_TOKEN_EXCHANGE_URL,
            data=params,
            headers=headers
            )
        self.access_token = response.json().get('access_token')
        self.expires_in = response.json().get('expires_in')
        self.ext = int(
            (datetime.datetime.now()+datetime.timedelta(
                seconds=int(self.expires_in))).timestamp()
            )

    def _get_user_info_by_token(self):
        headers = {
            'Authorization': OAUTH_AUTH_HEADER_TEMPLATE.format(
                token=self.access_token)}
        response = requests.get(YANDEX_USERINFO_API_URL, headers=headers)
        response_json = response.json()
        avatar_url = AVATAR_URL_TEMPLATE.format(
            avatar_id=response_json.get('default_avatar_id'),
            size=AVATAR_SIZE_CODE
        )
        user_id = response_json.get('id')
        jwt_token = jwt.encode(
            {
                'id': f'y_{user_id}',
                'ext': self.ext},
            JWT_SECRET,
            algorithm='HS256')

        return UserInfo(
            id=f'y_{user_id}',
            display_name=response_json.get('display_name'),
            is_avatar_empty=response_json.get('is_avatar_empty', True),
            default_avatar_url=avatar_url,
            token=jwt_token,
            expire=self.ext
        )
