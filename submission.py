from dataclasses import dataclass
from typing import List


@dataclass
class Submission:
    """Dataclass for song submission and result"""

    song: str
    artist: str
    submitter: str
    num_of_votes: int
    voters: dict

    def __str__(self) -> str:
        str_representation = [
            f"{self.song} - {self.artist} submitted by {self.submitter} with {self.num_of_votes} votes"
        ]
        for name, num_of_votes in self.voters.items():
            str_representation.append(f"{name} gave {num_of_votes} upvotes")
        return "\n".join(str_representation)
