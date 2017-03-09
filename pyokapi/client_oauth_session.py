from time import time


class ClientOAuthSession:
    def __init__(self, application, permissions):
        # TODO: проверка типов
        self.application = application
        self.permissions = ';'.join(map(lambda x: x.name, permissions))

    def start(self):
        if self.life_time > time() - self.start_time:
            return


