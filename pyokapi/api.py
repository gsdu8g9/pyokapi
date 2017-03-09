from urllib import request
from hashlib import md5

from .permissions import Permissions


class API:
    def __init__(self, session):
        self.session = session

    @staticmethod
    def _sig(parameters, session_secret_key):
        parameters_str = ''.join('{}={}'.format(key, value) for key, value in sorted(parameters.items(), key=lambda i: i[0]))

        return md5((parameters_str + session_secret_key).encode()).hexdigest()

    def _call_method(self, method, parameters):
        self.session.start()

        parameters.update({'application_key': self.session.application.key, 'method': method})
        parameters.update({
            'access_token': self.session.access_token,
            'sig': self._sig(
                parameters,
                md5((self.session.access_token + self.session.application.secret_key).encode()).hexdigest())
        })

        url = 'https://api.ok.ru/fb.do?' + '&'.join('{}={}'.format(key, value) for key, value in parameters.items())

        return request.urlopen(url).read().decode()

    def _users_has_app_permission(self, *, user_id=None, permission):
        if not isinstance(permission, Permissions):
            # TODO: Создать собственные классы ошибок, чтобы не повторять их текст
            raise TypeError("an Permissions is required (got type {})".format(permission.__class__.__name__))

        parameters = {'ext_perm': permission.name}

        if user_id:
            if not isinstance(user_id, str):
                raise TypeError("an string is required (got type {})".format(user_id.__class__.__name__))
            else:
                parameters['uid'] = user_id

        return self._call_method('users.hasAppPermission', parameters)