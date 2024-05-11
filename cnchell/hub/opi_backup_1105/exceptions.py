import utils

class REQUEST_FAILED(Exception):
    def __init__(self, message="Request Failed"):
        super().__init__(message)
    
class IO_ERROR(Exception):
    def __init__(self, message="IO Error"):
        super().__init__(message)

class NOT_FOUND(Exception):
    def __init__(self, message="Not Found"):
        super().__init__(message)

class CANCELED(Exception):
    def __init__(self, message="Canceled"):
        super().__init__(message)

class MACHINE_CONNECTION_ERROR(Exception):
    def __init__(self, message="Could not connect to machine"):
        super().__init__(message)