from bs4 import BeautifulSoup
from urllib import request, parse
from time import time

from .wizutils import cookie_jar


class AutoClientOAuthSession():
    def __init__(self, application, permissions, username, password, *, cookies_filename=None):
        # TODO: проверка типов
        self.application = application
        self.permissions = ';'.join(map(lambda x: x.name, permissions))

        self.life_time = 0
        self.start_time = 0
        self.access_token = None
        self.session_secret_key = None
        self.permissions_granted = []
        self.username = username
        self.password = password
        self.cookies_filename = cookies_filename

        # TODO: определить какие атрибуты используются только внутри класса, сделать из приватными, а внешние сделать
        # свойствами
        # TODO: реализовать менеджер контекстов, чтобы сохранять и загружать параметры сессии, чтобы не запрашивать
        # из лишний раз

    def start(self):
        if self.life_time > time() - self.start_time:
            return

        request.install_opener(
            request.build_opener(
                request.HTTPCookieProcessor(
                    cookie_jar(self.cookies_filename)
                )
            )
        )

        # Открытие диалога авторизации OAuth
        oauth_authorize_url = \
            'https://connect.ok.ru/oauth/authorize?' \
            'client_id={client_id}&scope={scope}&response_type=token&redirect_uri={redirect_uri}'.format(
                client_id=self.application.id,
                scope=self.permissions,
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
                'fr.email': self.username,
                'fr.password': self.password
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
                    scope=self.permissions,
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
        self.start_time = time()
        parameters = parse.parse_qs(parse.urlparse(page.geturl())[5])
        self.access_token = parameters['access_token'][0]
        self.session_secret_key = parameters['session_secret_key'][0]
        if 'permissions_granted' in parameters:
            self.permissions_granted = parameters['permissions_granted'][0].split(';')
        self.life_time = int(parameters['expires_in'][0])
