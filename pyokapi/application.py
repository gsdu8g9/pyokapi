class Application:
    def __init__(self, application_id, application_key, application_secret_key, redirect_uri):
        self.id = application_id
        self.key = application_key
        self.secret_key = application_secret_key
        self.redirect_uri = redirect_uri
