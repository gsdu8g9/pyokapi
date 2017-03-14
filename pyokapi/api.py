from hashlib import md5
import json
from urllib import request, parse


class API:
    def __init__(self, session):
        self.session = session
        self._method = []

    def __getattr__(self, item):
        self._method.append(item)

        return self

    def __call__(self, **kwargs):
        result = self._call_method('.'.join(self._method), **kwargs)
        self._method = []

        return result

    @staticmethod
    def _sig(parameters, session_secret_key):
        parameters_str = ''.join('{}={}'.format(key, value) for key, value in sorted(parameters.items(), key=lambda i: i[0]))

        return md5((parameters_str + session_secret_key).encode()).hexdigest()

    def _call_method(self, method, **kwargs):
        self.session.start()

        for name, value in list(kwargs.items()):
            if not value:
                del kwargs[name]

        kwargs.update({'application_key': self.session.application.key, 'method': method})
        kwargs.update({
            'access_token': self.session.access_token,
            'sig': self._sig(
                kwargs,
                md5((self.session.access_token + self.session.application.secret_key).encode()).hexdigest())
        })

        url = 'https://api.ok.ru/fb.do?' + parse.urlencode(kwargs)
        result = json.loads(request.urlopen(url).read().decode())

        # TODO: Внутренняя обработка ошибок
        # if isinstance(result, dict) and 'error_code' in result:
        #     if result['error_code'] == 10:
        #         raise OkAPIError("User must grant an access to permission '%s'" % result['error_data'].upper())

        return result
