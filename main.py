import os

from selenium import webdriver

from music_league_authenticator import MusicLeagueAuthenticator


def main():
    browser = get_chrome_browser()
    music_league_authenticator = MusicLeagueAuthenticator(browser)
    music_league_authenticator.authenticate()
    browser.quit()


def get_chrome_browser() -> webdriver.Chrome:
    # Get driver based on runtime environment
    if (
        os.environ.get("RUNTIME_ENV") != None
        and os.environ.get("RUNTIME_ENV").lower() == "prod"
    ):
        browser = webdriver.Chrome(executable_path="chromedriver_prod")
    else:
        browser = webdriver.Chrome()
    return browser


if __name__ == "__main__":
    main()
