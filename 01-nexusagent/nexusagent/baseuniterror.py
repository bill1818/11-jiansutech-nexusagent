class BaseUnitError(Exception):
    '''
    '''
    def __init__(self, message=''):
        super().__init__(message)
        self.error_message = message


class StatusSuccess(BaseUnitError):
    '''
    '''
    def __init__(self, message=''):
        super().__init__(message)


class StatusError(BaseUnitError):
    '''
    '''
    def __init__(self, message=''):
        super().__init__(message)

class UploadSuccess(BaseUnitError):
    '''
    '''
    def __init__(self, message=''):
        super().__init__(message)


class UploadError(BaseUnitError):
    '''
    '''
    def __init__(self, message=''):
        super().__init__(message)


class RegisterError(BaseUnitError):
    '''
    '''
    def __init__(self, message=''):
        super().__init__(message)


class ValueNull(BaseUnitError):
    '''
    '''
    def __init__(self, message=''):
        super().__init__(message)
