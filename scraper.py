import time

from selenium.webdriver import Chrome
from bs4 import BeautifulSoup

from exceptions import HTMLParserException


class Scraper:
    def __init__(self, browser: Chrome):
        self.browser = browser

    def scrape_rounds(self):
        round_results_links = self._get_rounds_hrefs()
        for round_name, link in round_results_links.items():
            print(f"Songs submitted for round {round_name}")
            self._get_round_results(link)
            print("=====================================================")

    def _get_rounds_hrefs(self):
        rounds_div_container = self._get_rounds_div_container()
        child_tags = rounds_div_container.contents
        round_results_hrefs = {}
        # 1st child is a <h4> tag with text "Completed Rounds"
        # For some reason second child is an empty string??
        # Start the loop at the 3rd element and grab all the hrefs
        MUSIC_LEAGUE_BASE_URL = "https://app.musicleague.com"
        for child_tag in child_tags[2:]:
            round_name = child_tag.find("h5").get_text()
            # hrefs are stored as relative urls so we need to prepend base url
            # First <a> tag is a link to the playlist and the second <a> tag is the results href
            round_result_href = (
                f"{MUSIC_LEAGUE_BASE_URL}{child_tag.find_all('a')[1]['href']}"
            )
            round_results_hrefs[round_name] = round_result_href

        for round_name, round_href in round_results_hrefs.items():
            print(f"{round_name} - {round_href}")

        return round_results_hrefs

    def _get_rounds_div_container(self):
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        h4_tags = soup.find_all("h4")
        completed_rounds = None
        for h4_tag in h4_tags:
            if h4_tag.get_text() == "Completed Rounds":
                completed_rounds = h4_tag

        if completed_rounds is None:
            raise HTMLParserException(
                f"Couldn't find 'Completed Rounds' on {self.browser.current_url}"
            )

        return completed_rounds.parent

    def _get_round_results(self, href):
        self.browser.get(href)
        # TODO: Need to figure out a way to find out when javascript has loaded round info
        time.sleep(5)
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        results_div_container = soup.find("div", class_="col-12 col-lg-8 offset-lg-2")
        child_divs = results_div_container.contents
        # First child div is the round name so we don't need it
        # Second child is an empty string?? idk why
        for child_div in child_divs[2:]:
            song_info_div_container = child_div.contents[0]
            song_info_div = song_info_div_container.contents[2]
            song_name = song_info_div.find("a").get_text()
            artist_name = song_info_div.find("span").get_text()
            print(f"{song_name} - {artist_name}")
