class OkAPIError(Exception):
    def __init__(self, response):
        self.code = response['error_code']
        self.data = response['error_data']
        self.message = response['error_msg']
        self.method = response['method']
        self.parameters = response['parameters']

        Exception.__init__(self, self.message)
