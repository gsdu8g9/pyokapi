from hashlib import md5
import json
from urllib import request, parse

from .errors import *
from .permissions import Permissions
from .typecheck import *


def _user_id(user_id):
    if user_id:
        if not is_user_id(user_id):
            raise OkAPIParamError('invalid uid value {}'.format(user_id))

    return user_id


def _user_ids(user_ids, max_len=None):
    if not is_user_ids_list(user_ids):
        if not is_user_id(user_ids):
            raise OkAPIParamError('invalid uids value {}'.format(user_ids))

        user_ids = [user_ids]

    if max_len and max_len < len(user_ids):
        raise Exception  # TODO: OkAPIParamError()

    return ','.join(user_ids)


def _methods_list(methods_list):
    if not is_methods_list(methods_list):
        if not isinstance(methods_list, str):
            raise OkAPIParamError('invalid methods value {}'.format(methods_list))

        methods_list = [methods_list]

    return ','.join(methods_list)


def _permission(permission):
    if not isinstance(permission, Permissions):
        raise OkAPIParamError('invalid ext_perm value {}'.format(permission))

    return permission.name


class API:
    class _users:
        def __init__(self, api):
            self.api = api

        def deleteGuests(self, *, uids):
            return self.api._call_method('users.deleteGuests', uids=_user_ids(uids))

        def getAdditionalInfo(self, *, uids):
            return self.api._call_method('users.getAdditionalInfo', uids=_user_ids(uids, 100))

        def getCallsLeft(self, *, uid=None, methods):
            return self.api._call_method('users.getCallsLeft', uid=_user_id(uid), methods=_methods_list(methods))

        def hasAppPermission(self, *, uid=None, ext_perm):
            return self.api._call_method('users.hasAppPermission', uid=_user_id(uid), ext_perm=_permission(ext_perm))

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

        for name, value in list(parameters.items()):
            if not value:
                del parameters[name]

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
