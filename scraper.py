import time
from typing import Dict

from selenium.webdriver import Chrome
from bs4 import BeautifulSoup

from exceptions import HTMLParserException
from submission import Submission


class Scraper:
    def __init__(self, browser: Chrome):
        self.browser = browser

    def scrape_rounds(self) -> Dict:
        round_results_links = self._get_rounds_hrefs()
        rounds = {}
        for round_name, link in round_results_links.items():
            print(f"Getting rounds results for {round_name}")
            rounds[round_name] = self._get_round_results(link)

        return rounds

    def _get_rounds_hrefs(self):
        print("Getting links for all completed rounds")
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
        submission_divs = results_div_container.contents
        submissions = []
        # First child div is the round name so we don't need it
        # Second child is an empty string?? idk why
        for submission_div in submission_divs[2:]:
            song_name = self._get_song_name(submission_div)
            artist_name = self._get_artist_name(submission_div)
            submitter_name = self._get_submitter_name(submission_div)
            number_of_votes = self._get_number_of_votes(submission_div)
            voters = self._get_voters(submission_div)
            submission = Submission(
                song_name, artist_name, submitter_name, number_of_votes, voters
            )
            submissions.append(submission)

        return submissions

    def _get_song_name(self, submission_div):
        song_info_div_container = submission_div.contents[0]
        song_info_div = song_info_div_container.contents[2]
        song_name = song_info_div.find("a").get_text()

        return song_name

    def _get_artist_name(self, submission_div):
        song_info_div_container = submission_div.contents[0]
        song_info_div = song_info_div_container.contents[2]
        artist_name = song_info_div.find("span").get_text()

        return artist_name

    def _get_submitter_name(self, submission_div):
        submitter_info_div_container = submission_div.contents[2]
        submitter_name_info = submitter_info_div_container.find("span").get_text()
        # This 'Submitted by ' text appears in the span so we take the text after it
        submitter_name = submitter_name_info.split("Submitted by ")[1]

        return submitter_name

    def _get_number_of_votes(self, submission_div):
        song_info_div_container = submission_div.contents[0]
        voting_info_div = song_info_div_container.contents[4]
        number_of_votes = voting_info_div.find("span").get_text()

        # First character of number_of_votes is + so we just take the 10 from number_of_votes = '+10'
        return number_of_votes[1:]

    def _get_voters(self, submission_div):
        voters = {}
        # voter divs start at the 5th div and each div holds voter info
        for voter_div_container in submission_div.contents[4:]:
            voter_name = voter_div_container.find("span", class_="fs-6").get_text()
            spans = voter_div_container.find_all("span")
            num_of_upvotes = 0
            for span in spans:
                # If the text has a + its the nubmer of upvtes. Chop of '+' and just take the number
                if "+" in span.get_text():
                    num_of_upvotes = span.get_text()[1:]
                    break

            # If someone comments they still show up as a child element of the submission_div
            # But where the '+' would normally go is an empty span so we won't include them in the voters
            if num_of_upvotes == 0:
                continue

            voters[voter_name] = num_of_upvotes

        return voters
