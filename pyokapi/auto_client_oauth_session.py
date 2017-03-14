import os.path
import pickle
import requests
from urllib import parse


from bs4 import BeautifulSoup
from time import time


class AutoClientOAuthSession:
    def __init__(self, application, permissions, username, password, *, session_data_filename=None):
        self.application = application
        self.access_token = None

        if not isinstance(permissions, list):
            permissions = [permissions]
        self._permissions = ';'.join(permissions)
        self._username = username
        self._password = password
        self._session_data_filename = session_data_filename

        self._cookies = None
        self._life_time = 0
        self._start_time = 0
        self._session_secret_key = None
        self._permissions_granted = []

        # TODO:
        # - Обработка ошибок при залогинивании и ошибок сервера
        # - Реализовать полное обновление сессии при изменении аргументов инициализации

    def __enter__(self):
        if self._session_data_filename and os.path.isfile(self._session_data_filename):
            with open(self._session_data_filename, 'rb') as session_data_file:
                self.__dict__.update(pickle.load(session_data_file))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session_data_filename:
            with open(self._session_data_filename, 'wb') as session_data_file:
                pickle.dump({
                    'access_token': self.access_token,
                    '_cookies': self._cookies,
                    '_life_time': self._life_time,
                    '_start_time': self._start_time
                }, session_data_file)

    def start(self):
        if self._life_time > time() - self._start_time:
            return

        # Открытие диалога авторизации OAuth
        oauth_authorize_url = \
            'https://connect.ok.ru/oauth/authorize?' \
            'client_id={client_id}&scope={scope}&response_type=token&redirect_uri={redirect_uri}'.format(
                client_id=self.application.id,
                scope=self._permissions,
                redirect_uri=self.application.redirect_uri
            )
        response = requests.get(oauth_authorize_url, cookies=self._cookies)

        # Залогинивание
        if 'st.cmd=OAuth2Login' in response.url:
            soup = BeautifulSoup(response.text, 'lxml')
            url = 'https://connect.ok.ru' + soup.form.get('action')
            data = {
                'fr.posted': 'set',
                'fr.remember': 'on',
                'fr.email': self._username,
                'fr.password': self._password
            }
            response = requests.post(url, data)

        # Разрешение прав доступа
        if response.url == oauth_authorize_url or 'st.cmd=OAuth2Permissions' in response.url:
            soup = BeautifulSoup(response.text, 'lxml')
            url = \
                'https://connect.ok.ru/dk?' \
                'st.cmd=OAuth2Permissions&st.scope={scope}&st.response_type=token&st.show_permissions=off&' \
                'st.redirect_uri={redirect_uri}&st.client_id={client_id}&cmd=OAuth2Permissions'.format(
                    client_id=self.application.id,
                    scope=self._permissions,
                    redirect_uri=self.application.redirect_uri
                )
            data = {
                'fr.posted': 'set',
                'fr.token': soup.find('input', {'name': 'fr.token'}).get('value'),
                'button_accept_request': None
            }
            response = requests.post(url, data)

        # Получение access_token
        self._start_time = time()
        parameters = parse.parse_qs(parse.urlparse(response.url)[5])
        self.access_token = parameters['access_token'][0]
        self._session_secret_key = parameters['session_secret_key'][0]
        if 'permissions_granted' in parameters:
            self._permissions_granted = parameters['permissions_granted'][0].split(';')
        self._life_time = int(parameters['expires_in'][0])

        self._cookies = response.cookies
