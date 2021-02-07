class TeamExists(Exception):
    """
    Exception raised for errors in creating new team using existing team name
    """

    def __init__(self, message="Team with name exists"):
        super().__init__(message)

class TeamNotFound(Exception):
    """
    Exception raised for when team is not found
    """

    def __init__(self, message="Team Not Found"):
        super().__init__(message)

class UserExistInTeam(Exception):
    """
    Exception raised when duplicate user is added to team
    """

    def __init__(self, message="User exist in team already"):
        super().__init__(message)

class InvalidTeamName(Exception):
    """
    Exception raised when team name is not supported
    """

    def __init__(self, message="User exist in team already"):
        super().__init__(message)
