import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from music_league_authenticator import MusicLeagueAuthenticator
from scraper import Scraper
from s3_service import S3Service

def handler(event, context):
    main()

def main():
    try:
        browser = get_chrome_browser()
        music_league_authenticator = MusicLeagueAuthenticator(browser)
        music_league_authenticator.authenticate()
        scraper = Scraper(browser)
        s3_service = S3Service()
        rounds_results = scraper.scrape_rounds(ignore=s3_service.existing_round_links)
        _pretty_print_rounds_results(rounds_results)
        s3_service.write_rounds_results(rounds_results)
    finally:
        browser.quit()


def get_chrome_browser() -> webdriver.Chrome:
    # Get driver based on runtime environment
    if (
        os.environ.get("RUNTIME_ENV") != None
        and os.environ.get("RUNTIME_ENV").lower() == "prod"
    ): # Prod driver is packed into lambda layer
        options = Options()
        options.binary_location = '/opt/headless-chromium'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--single-process')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome('/opt/chromedriver',options=options)
    else:
        # Local chrome dirver for development. Should be named 'chromedriver'
        return webdriver.Chrome()

def _pretty_print_rounds_results(rounds_results):
    for round in rounds_results:
        print(round['round_name'])
        for submission in round['results']:
            print(
                f"{submission['song']} - {submission['artist']} submitted by {submission['submitter_name']} with {submission['number_of_votes']} votes"
            )
            for voter in submission["voters"]:
                num_of_votes = voter['num_of_votes']
                name = voter['voter_name']
                if num_of_votes == 1 or num_of_votes == -1:
                    print(f"{name} gave {num_of_votes} upvote")
                else:
                    print(f"{name} gave {num_of_votes} upvotes")
            print("\n")
        print("=" * 50)


if __name__ == "__main__":
    main()