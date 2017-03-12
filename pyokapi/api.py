from hashlib import md5
import json
from urllib import request, parse
from .errors import *

from .permissions import Permissions


class API:
    class _users:
        def __init__(self, api):
            self.api = api

        def deleteGuests(self, *, user_ids):
            if not (isinstance(user_ids, list) and all(map(lambda x: isinstance(x, str), user_ids))):
                raise TypeError('a list of strings is required')

            return self.api._call_method('users.deleteGuests', uids=','.join(user_ids))

        def getAdditionalInfo(self, *, user_ids):
            if not (isinstance(user_ids, list) and all(map(lambda x: isinstance(x, str), user_ids))):
                raise TypeError('a list of strings is required')

            if len(user_ids) > 100:
                raise Exception  # TODO: OkAPIParamError()

            return self.api._call_method('users.getAdditionalInfo', uids=','.join(user_ids))

        def getCallsLeft(self, *, user_id=None, methods):
            if not (isinstance(methods, list) and all(map(lambda x: isinstance(x, str), methods))):
                raise TypeError('a list of strings is required')

            parameters = {'methods': ','.join(methods)}

            if user_id:
                if not isinstance(user_id, str):
                    raise TypeError('a string is required')

                parameters['uid'] = user_id

            return self.api._call_method('users.getCallsLeft', **parameters)

        def hasAppPermission(self, *, user_id=None, permission):
            if not isinstance(permission, Permissions):
                # TODO: Создать собственные классы ошибок, чтобы не повторять их текст
                raise TypeError('a Permissions is required')

            parameters = {'ext_perm': permission.name}

            if user_id:
                if not isinstance(user_id, str):
                    raise TypeError('a string is required')

                parameters['uid'] = user_id

            return self.api._call_method('users.hasAppPermission', **parameters)

    def __init__(self, session):
        self.session = session
        self._method = []

        self.users = API._users(self)

    @staticmethod
    def _sig(parameters, session_secret_key):
        parameters_str = ''.join('{}={}'.format(key, value) for key, value in sorted(parameters.items(), key=lambda i: i[0]))

        return md5((parameters_str + session_secret_key).encode()).hexdigest()

    def _call_method(self, method, **parameters):
        self.session.start()

        parameters.update({'application_key': self.session.application.key, 'method': method})
        parameters.update({
            'access_token': self.session.access_token,
            'sig': self._sig(
                parameters,
                md5((self.session.access_token + self.session.application.secret_key).encode()).hexdigest())
        })

        url = 'https://api.ok.ru/fb.do?' + parse.urlencode(parameters)
        result = json.loads(request.urlopen(url).read().decode())

        if isinstance(result, dict) and 'error_code' in result:
            if result['error_code'] == 10:
                raise OkAPIPermissionDeniedError("User must grant an access to permission '%s'" % result['error_data'].upper())

        return result
