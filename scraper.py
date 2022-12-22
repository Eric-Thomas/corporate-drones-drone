import time
from typing import Dict
import bs4

from selenium.webdriver import Chrome
from bs4 import BeautifulSoup

from exceptions import HTMLParserException


class Scraper:
    def __init__(self, browser: Chrome):
        self.browser = browser

    def scrape_rounds(self, ignore) -> Dict:
        rounds_details = self._get_rounds_details()
        rounds = []
        # each item in items should be {"round_name" :  $ROUND_NAME, "playlist_link" : $LINK, "results": [LIST_OF_RESULTS]}
        for round in rounds_details:
            if round['round_name'] in ignore:
                print(f"{round['round_name']} has already been scraped. Skipping")
                continue
            print(f"Getting rounds results for {round['round_name']}")
            round_item = {}
            round_item['round_name'] = round['round_name']
            round_item["playlist_link"] = round['round_playlist_href']
            round_item["results"] = []
            round_result = self._get_round_results(round['round_href'])
            round_item['results'] = round_result
            rounds.append(round_item)

        return rounds

    def _get_rounds_details(self):
        print("Getting links for all completed rounds")
        rounds_div_container = self._get_rounds_div_container()
        child_tags = rounds_div_container.contents
        rounds = []
        # 1st child is a <h4> tag with text "Completed Rounds"
        # For some reason second child is an empty string??
        # Start the loop at the 3rd element and grab all the hrefs
        MUSIC_LEAGUE_BASE_URL = "https://app.musicleague.com"
        for child_tag in child_tags[2:]:
            round_details = {}
            round_name = child_tag.find("h5").get_text()
            round_details['round_name'] = round_name
            # hrefs are stored as relative urls so we need to prepend base url
            # First <a> tag is a link to the playlist and the second <a> tag is the results href
            links = child_tag.find_all('a')
            round_result_href = (
                f"{MUSIC_LEAGUE_BASE_URL}{links[1]['href']}"
            )
            round_details['round_href'] = round_result_href
            # First link is link to playlist
            round_details['round_playlist_href'] = links[0]['href']
            rounds.append(round_details)

        for round in rounds:
            print(f"{round['round_name']} - {round['round_href']}, {round['round_playlist_href']}")

        return rounds

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
            # Each submission should be {"song": $SONG, "artist": $ARTIST, "submitter_name": $NAME, "number_of_votes": $NUM, "voters": [{"voter_name": $NAME, "num_of_votes": $NUM}]}
            submission = {}
            submission["song"] = self._get_song_name(submission_div)
            submission["artist"] = self._get_artist_name(submission_div)
            submission["submitter_name"] = self._get_submitter_name(submission_div)
            submission["number_of_votes"] = self._get_number_of_votes(submission_div)
            submission["voters"] = self._get_voters(submission_div)
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

        # Convert number of votes to an int. Votes can be positive or negative
        return int(str(number_of_votes))

    def _get_voters(self, submission_div):
        voters = []
        # voter divs start at the 5th div and each div holds voter info
        for voter_div_container in submission_div.contents[4:]:
            voter_name = voter_div_container.find("span", class_="fs-6").get_text()
            try:
                voter_span = voter_div_container.find("span", class_="fs-5")
                num_of_votes = 0
                # When it is a positive number of votes, the vote number is nested in a span within a span
                # Ex:
                # 
                # <span class="d-inline-block align-middle mx-2 fs-5">
                #   <span class="">+1</span>
                # </span>
                if isinstance(voter_span.contents[0], bs4.element.Tag):
                    num_of_votes = int(str(voter_span.contents[0].contents[0]))

                # When it is a negative number of votes, the vote number is the contents of the fs-5 span
                # <span class="d-inline-block align-middle mx-2 fs-5" style="color: red;">-1</span>
                else:
                    num_of_votes = int(str(voter_span.contents[0]))

                voter = {}
                voter['voter_name'] = voter_name
                voter['num_of_votes'] = num_of_votes
                voters.append(voter)
            except AttributeError:
                # If someone comments they still show up as a child element of the submission_div
                # However there will be no span with class fs-5 so we get attribute error
                # We don't add them to the number of voters since they just commented
                continue

        return voters
