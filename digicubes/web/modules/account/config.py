"""
DigiCubes Web Defaults
"""


class AccountConfig:
    TOKEN_COOKIE_NAME: str = "digicubes.token"
    TOKEN_SESSION_NAME: str = "digicubes.token"

    DIGICUBES_ACCOUNT_LOGIN_VIEW: str = "account.login"
    DIGICUBES_ACCOUNT_REGISTER_VIEW: str = "account.register"
    DIGICUBES_ACCOUNT_INDEX_VIEW: str = "account.index"
    DIGICUBES_ACCOUNT_URL_PREFIX: str = "/account"