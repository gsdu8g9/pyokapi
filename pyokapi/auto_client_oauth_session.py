from bs4 import BeautifulSoup
from urllib import request, parse
from time import time

from .wizutils import cookie_jar  # TODO: Подумать надо над именем модуля и функции


class AutoClientOAuthSession:
    def __init__(self, application, permissions, username, password, *, cookies_filename=None):
        self.application = application
        self.access_token = None

        self._permissions = ';'.join(permissions)
        self._username = username
        self._password = password
        self._cookies_filename = cookies_filename

        self._life_time = 0
        self._start_time = 0
        self._session_secret_key = None
        self._permissions_granted = []

        # TODO:
        # - Реализовать менеджер контекстов, чтобы сохранять и загружать параметры сессии, чтобы не запрашивать из
        # лишний раз
        # - Сохранять все данные в файл используя модуль pickle вклюая куки

    def start(self):
        if self._life_time > time() - self._start_time:
            return

        request.install_opener(
            request.build_opener(
                request.HTTPCookieProcessor(
                    cookie_jar(self._cookies_filename)
                )
            )
        )

        # Открытие диалога авторизации OAuth
        oauth_authorize_url = \
            'https://connect.ok.ru/oauth/authorize?' \
            'client_id={client_id}&scope={scope}&response_type=token&redirect_uri={redirect_uri}'.format(
                client_id=self.application.id,
                scope=self._permissions,
                redirect_uri=self.application.redirect_uri
            )
        page = request.urlopen(oauth_authorize_url)

        # Залогинивание
        if 'st.cmd=OAuth2Login' in page.geturl():
            soup = BeautifulSoup(page.read(), 'lxml')
            url = 'https://connect.ok.ru' + soup.form.get('action')
            query = {
                'fr.posted': 'set',
                'fr.remember': 'on',
                'fr.email': self._username,
                'fr.password': self._password
            }
            data = parse.urlencode(query).encode('ascii')
            page = request.urlopen(url, data)

        # Разрешение прав доступа
        if page.geturl() == oauth_authorize_url or 'st.cmd=OAuth2Permissions' in page.geturl():
            soup = BeautifulSoup(page.read(), 'lxml')
            url = \
                'https://connect.ok.ru/dk?' \
                'st.cmd=OAuth2Permissions&st.scope={scope}&st.response_type=token&st.show_permissions=off&' \
                'st.redirect_uri={redirect_uri}&st.client_id={client_id}&cmd=OAuth2Permissions'.format(
                    client_id=self.application.id,
                    scope=self._permissions,
                    redirect_uri=self.application.redirect_uri
                )
            query = {
                'fr.posted': 'set',
                'fr.token': soup.find('input', {'name': 'fr.token'}).get('value'),
                'button_accept_request': None
            }
            data = parse.urlencode(query).encode('ascii')
            page = request.urlopen(url, data)

        # Получение access_token
        self._start_time = time()
        parameters = parse.parse_qs(parse.urlparse(page.geturl())[5])
        self.access_token = parameters['access_token'][0]
        self._session_secret_key = parameters['session_secret_key'][0]
        if 'permissions_granted' in parameters:
            self._permissions_granted = parameters['permissions_granted'][0].split(';')
        self._life_time = int(parameters['expires_in'][0])
