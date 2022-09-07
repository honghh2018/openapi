from typing import Optional

from openapi.providers.base import BaseClient, BaseResult, Token
from openapi.exceptions import DisallowedHost
from openapi.enums import IntegerChoices


class Code(IntegerChoices):
    FAIL = -1, '失败'
    SUCCESS = 0, '成功'
    INVALID_WHITE_LIST = 40164, 'ip 未在白名单'


class Result(BaseResult):
    errcode: int = Code.SUCCESS_CODE
    errmsg: Optional[str]
    msgid: Optional[int]


class Client(BaseClient):
    NAME = '微信服务号'
    API_BASE_URL = 'https://api.weixin.qq.com/cgi-bin'
    API_VERSION = ''

    def __init__(self, app_id, secret):
        super().__init__()
        self.app_id = app_id
        self.secret = secret
        self.codes = Code

    def request(
        self, method, endpoint, params=None, data=None,
        token_request=False
    ):
        if not token_request:
            if params is None:
                params = {}
            params['access_token'] = self.access_token

        request_url = f'{self.API_BASE_URL}{endpoint}'
        response = self._request(
            method, request_url,
            params=params, json=data
        )
        if response is None:
            Result(code=self.codes.FAIL)

        result = response.json()
        if 'errcode' in result:
            return Result(**result)
        else:
            return Result(data=result)

    def fetch_access_token(self):
        result = self.request(
            'get', '/token', params={
                'grant_type': 'client_credential',
                'appid': self.app_id,
                'secret': self.secret
            },
            token_request=True
        )
        if result.errcode == self.codes.SUCCESS:
            self._token = Token(**result.data)

        if result.errcode == self.codes.INVALID_WHITE_LIST:
            raise DisallowedHost(result.errmsg)
