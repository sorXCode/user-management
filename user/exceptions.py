class BaseException(Exception):
    def __init__(self, message="User with email exists"):
        super().__init__(message)

class UserExists(BaseException):
    """
    Exception raised for errors in creating new user using existing email
    """
    pass

class UserNotFound(BaseException):
    """
    Exception raised for non existing user
    """
    pass

class InvalidPassword(BaseException):
    pass