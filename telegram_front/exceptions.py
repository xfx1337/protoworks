class InvalidConfig(Exception):
    pass

class DatabaseInitFailed(Exception):
    pass

class REQUEST_FAILED(Exception):
    def __init__(self, message="Ошибка запроса", no_message=True):
        super().__init__(message)