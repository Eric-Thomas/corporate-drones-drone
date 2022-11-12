class NoSpotifyUsernameException(Exception):
    """Exception raised when spotify username is not provided in env variables"""

    def __init__(
        self,
        message="SPOTIFY_USERNAME environment variable not found. Export SPOTIFY_USERNAME in env variables",
    ):
        self.message = message
        super().__init__(self.message)


class NoSpotifyPasswordException(Exception):
    """Exception raised when spotify password is not provided in env variables"""

    def __init__(
        self,
        message="SPOTIFY_PASSWORD environment variable not found. Export SPOTIFY_PASSWORD in env variables",
    ):
        self.message = message
        super().__init__(self.message)


class SpotifyAuthenticationException(Exception):
    """Exception raised when spotify authentication failed"""

    def __init__(
        self,
        message="Authentication failed with spotify. Please check SPOTIFY_USERNAME and SPOTIFY_PASSWORD are correct",
    ):
        self.message = message
        super().__init__(self.message)


class HTMLParserException(Exception):
    """Exception raised when spotify authentication failed"""

    def __init__(
        self,
        message="Error parsing HTML",
    ):
        self.message = message
        super().__init__(self.message)
