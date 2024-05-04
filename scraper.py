import time
from typing import Dict, List
import bs4

from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
from bs4.element import Tag, PageElement

from exceptions import HTMLParserException


class Scraper:
    def __init__(self, browser: Chrome):
        self.browser = browser

    def scrape_rounds(self, ignore) -> Dict:
        rounds_details = self._get_rounds_details()
        rounds = []
        # each item in items should be {"round_name" :  $ROUND_NAME, "playlist_link" : $LINK, "results": [LIST_OF_RESULTS]}
        for round in rounds_details:
            # Ignore rounds already scraped
            if round["round_href"] in ignore:
                print(f"{round['round_name']} has already been scraped. Skipping")
                continue
            print(f"Getting rounds results for {round['round_name']}")
            round_item = {}
            round_item["round_name"] = round["round_name"]
            round_item["playlist_link"] = round["round_playlist_href"]
            round_item["round_href"] = round["round_href"]
            round_item["results"] = []
            round_result = self._get_round_results(round["round_href"])
            round_item["results"] = round_result
            rounds.append(round_item)

        return rounds

    def _get_rounds_details(self):
        print("Getting links for all completed rounds")
        rounds_div_container = self._get_rounds_div_container()
        child_tags = rounds_div_container.contents
        rounds = []
        # The 19th element is the start of all the completed rounds
        MUSIC_LEAGUE_BASE_URL = "https://app.musicleague.com"
        ROUND_RESULT_HREF_INDEX = 3
        SPOTIFY_PLAYLIST_HREF_INDEX = 2
        for child_tag in child_tags[18:]:
            # Not sure why ever other child tag is a newline character
            if child_tag == "\n":
                continue
            round_details = {}
            round_name = child_tag.find("h5").get_text()
            round_details["round_name"] = round_name
            # hrefs are stored as relative urls so we need to prepend base url
            # First <a> tag is a link to the playlist and the second <a> tag is the results href
            links = child_tag.find_all("a")
            round_result_href = (
                f"{MUSIC_LEAGUE_BASE_URL}{links[ROUND_RESULT_HREF_INDEX]['href']}"
            )
            # Remove last / to keep hrefs consistent
            if round_result_href[-1] == "/":
                round_result_href = round_result_href[:-1]
            round_details["round_href"] = round_result_href
            # First link is link to playlist
            round_details["round_playlist_href"] = links[SPOTIFY_PLAYLIST_HREF_INDEX][
                "href"
            ]
            rounds.append(round_details)

        for round in rounds:
            print(
                f"{round['round_name']} - {round['round_href']}, {round['round_playlist_href']}"
            )

        return rounds

    def _get_rounds_div_container(self):
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        h5_tags = soup.find_all("h5")
        completed_rounds = None
        for h5_tag in h5_tags:
            if h5_tag.get_text() == "Completed Rounds":
                completed_rounds = h5_tag

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
        results_div_container = soup.find_all(
            "div", class_="col-12 col-lg-8 offset-lg-2"
        )
        # skip first element which is the round title info
        submission_divs: List[Tag] = results_div_container[1].contents
        submissions = []
        # First child div is the round name so we don't need it
        # Second child is an empty string?? idk why
        for submission_div in submission_divs[2:]:
            if submission_div == "\n":
                continue
            # Each submission should be {"song": $SONG, "artist": $ARTIST, "submitter_name": $NAME, "number_of_votes": $NUM, "voters": [{"voter_name": $NAME, "num_of_votes": $NUM}]}
            submission = {}
            submission["song"] = self._get_song_name(submission_div)
            submission["artist"] = self._get_artist_name(submission_div)
            submission["submitter_name"] = self._get_submitter_name(submission_div)
            submission["number_of_votes"] = self._get_number_of_votes(submission_div)
            submission["voters"] = self._get_voters(submission_div)
            submissions.append(submission)

        return submissions

    def _get_song_name(self, submission_div: Tag) -> str:
        song_info_div_container: Tag = submission_div.contents[1]
        song_info_div: Tag = song_info_div_container.contents[1]
        song_name = song_info_div.find("h6").get_text()

        return song_name

    def _get_artist_name(self, submission_div: Tag) -> str:
        song_info_div_container: Tag = submission_div.contents[1]
        song_info_div: Tag = song_info_div_container.contents[1]
        artist_name = song_info_div.find(
            "p", class_="card-text m-0 text-truncate"
        ).get_text()

        return artist_name

    def _get_submitter_name(self, submission_div: Tag) -> str:
        submitter_info_div_container: Tag = submission_div.contents[1]
        submitter_name: Tag = submitter_info_div_container.find(
            "h6", class_="m-0 text-truncate text-body fw-semibold"
        ).get_text()

        return submitter_name

    def _get_number_of_votes(self, submission_div: Tag) -> int:
        song_info_div_container: Tag = submission_div.contents[1]
        number_of_votes: str = (
            song_info_div_container.find("h3", class_="m-0").get_text().strip()
        )

        # When a person doesn't vote the number of votes is of the form
        # '<number of votes>\n           <numbe of votes removing upvotes>
        if "\n" in number_of_votes:
            number_of_votes = number_of_votes.split()[0]

        # Convert number of votes to an int. Votes can be positive or negative
        return int(number_of_votes)

    def _get_voters(self, submission_div: Tag):
        voters = []
        # Case for when no one votes or comments:
        if len(submission_div.contents) < 6:
            return voters
        # voter divs start at the 6th div and each div holds voter info
        voter_div_container: List[Tag] = submission_div.contents[5].contents
        for voter_row in voter_div_container:
            if voter_row == "\n":
                continue
            voter_name = voter_row.find(
                "b", class_="d-block text-truncate text-body"
            ).get_text()
            try:
                num_of_votes = int(voter_row.find("h6", class_="m-0").get_text())
                voter = {}
                voter["voter_name"] = voter_name
                voter["num_of_votes"] = num_of_votes
                voters.append(voter)
            except AttributeError:
                # If someone comments they still show up as a child element of the submission_div
                # However there will be no span with class fs-5 so we get attribute error
                # We don't add them to the number of voters since they just commented
                continue

        return voters
