import utils

class REQUEST_FAILED(Exception):
    def __init__(self, message="Ошибка запроса", no_message=False):
        super().__init__(message)
        if not no_message:
            utils.message(message)
    
class IO_ERROR(Exception):
    def __init__(self, message="Ошибка IO", no_message=False):
        super().__init__(message)
        if not no_message:
            utils.message(message)

class NOT_FOUND(Exception):
    def __init__(self, message="Не найдено ", text="", no_message=False):
        super().__init__(message)
        if not no_message:
            utils.message(message + text)

class CANCELED(Exception):
    def __init__(self, message="Отменено", text="", no_message=False):
        super().__init__(message)
        if not no_message:
            utils.message(message + text)