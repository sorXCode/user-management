class TeamExists(Exception):
    """
    Exception raised for errors in creating new team using existing team name
    """

    def __init__(self, message="Team with name exists"):
        super().__init__(message)

class TeamNotFound(Exception):
    """
    Exception raised for errors in creating new team using existing team name
    """

    def __init__(self, message="Team Not Found"):
        super().__init__(message)
