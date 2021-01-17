class UserExists(Exception):
    """
    Exception raised for errors in creating new user using existing email
    """

    def __init__(self, message="User with email exists"):
        super().__init__(message)


class UserNotFound(Exception):
    """
    Exception raised for non existing user
    """

    def __init__(self, message="User Not Found"):
        super().__init__(message)


class InvalidPassword(Exception):

    def __init__(self, message="Invalid password"):
        super().__init__(message)
