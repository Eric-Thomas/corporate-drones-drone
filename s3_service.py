import json

import boto3
from botocore.exceptions import ClientError

S3_BUCKET = "corporate-drones-music-league"
OBJECT_KEY = "music_league_rounds.json"


class S3Service:
    def __init__(self):
        self.client = boto3.client("s3")
        self.existing_json_body = self.get_existing_json_body()
        self.existing_round_links = self.get_existing_rounds_links()

    def get_existing_json_body(self):
        try:
            return json.load(
                self.client.get_object(Bucket=S3_BUCKET, Key=OBJECT_KEY)["Body"]
            )
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "NoSuchKey":
                print("No object found - returning default json")
                return {"rounds": []}
            else:
                raise

    def get_existing_rounds_links(self):
        print("Getting existing rounds")
        existing_rounds = []
        for round in self.existing_json_body["rounds"]:
            print(f"existing round {round['round_name']} - {round['round_href']}")
            existing_rounds.append(round["round_href"])

        return existing_rounds

    def write_rounds_results(self, rounds_results):
        # Don't want to overwrite existing rounds so we initiate response with existing rounds
        body = {"rounds": self.existing_json_body["rounds"]}
        print("Adding new rounds to existing json...")
        # Add newly scraped rounds
        body["rounds"].extend(rounds_results)
        object_bytes = json.dumps(body).encode("utf-8")
        print(f"Pushing to {S3_BUCKET} with key {OBJECT_KEY}...")
        # self.client.put_object(Body=object_bytes, Bucket=S3_BUCKET, Key=OBJECT_KEY)
        self.client.put_object(Body=object_bytes, Bucket=S3_BUCKET, Key=OBJECT_KEY)
        print("Successfully pushed to s3")
