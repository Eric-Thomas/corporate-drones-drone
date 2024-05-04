import time
import os

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from exceptions import (
    NoSpotifyUsernameException,
    NoSpotifyPasswordException,
    SpotifyAuthenticationException,
)
from secret_manager_service import get_spotify_password


class MusicLeagueAuthenticator:

    CORPORATE_DRONES_URL = "https://app.musicleague.com/l/4b82d7c3ca0e4d5db2d9807e3f1da0cc"
    DICTATOR_LEAGUE_URL = "https://app.musicleague.com/l/65b91ad3889548ed8fd68315754def8e"
    THIRD_TIMES_THE_MAKE_URL = "https://app.musicleague.com/l/096d271749b4471e8f80d79f4b5ce50d/"
    THE_LEAGUE_IS_SO_BACK_URL = "https://app.musicleague.com/l/b7012bad0fa341fdb523b18bfb83d03a"

    def __init__(self, browser: Chrome):
        self.browser = browser

    def authenticate(self, callback_url=THE_LEAGUE_IS_SO_BACK_URL):
        self.browser.get(callback_url)
        self._go_to_spotify_login()
        self._enter_spotify_credentials()
        time.sleep(2)
        self._validate_login()
        self._agree_to_authenticate()

    def _go_to_spotify_login(self):
        login_button = self.browser.find_element(By.LINK_TEXT, "Log in with Spotify")
        print("Clicking on login button")
        login_button.click()

    def _enter_spotify_credentials(self):
        print("Entering username and password")
        username_field = self.browser.find_element(By.ID, "login-username")
        username = self._get_username()
        username_field.send_keys(username)
        password_field = self.browser.find_element(By.ID, "login-password")
        password = self._get_passowrd()
        password_field.send_keys(password)
        print("Authenticating")
        spotify_login_button = self.browser.find_element(By.ID, "login-button")
        spotify_login_button.click()

    def _get_username(self):
        if os.environ.get("SPOTIFY_USERNAME") is None:
            raise NoSpotifyUsernameException()

        return os.environ.get("SPOTIFY_USERNAME")

    def _get_passowrd(self):
        # fetch secret from aws secrets manager if in prod
        if os.environ.get("RUNTIME_ENV") == "prod":
            os.environ['SPOTIFY_PASSWORD'] = get_spotify_password()

        if os.environ.get("SPOTIFY_PASSWORD") is None:
            raise NoSpotifyPasswordException()

        return os.environ.get("SPOTIFY_PASSWORD")

    def _validate_login(self):
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        if "Agree" not in soup.get_text():
            raise SpotifyAuthenticationException()

    def _agree_to_authenticate(self):
        agree_button = self.browser.find_element(
            By.CSS_SELECTOR, 'button[data-testid="auth-accept"]'
        )
        agree_button.click()
        time.sleep(5)
