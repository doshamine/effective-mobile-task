from enum import Enum, unique

@unique
class TokenType(Enum):
    ACCESS = 'access_token'
    REFRESH = 'refresh_token'