class UserAlreadyExistsError(Exception):
    pass 

class UserNotFoundError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class InvalidRefreshTokenError(Exception):
    pass

class InvalidAccessTokenError(Exception):
    pass