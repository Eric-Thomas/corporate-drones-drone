import json

import boto3

S3_BUCKET = "corporate-drones-music-league"
OBJECT_KEY = "dictator_league.json"


class S3Service:
    def __init__(self):
        self.client = boto3.client("s3")
        self.existing_json_body = self.get_existing_json_body()
        self.existing_round_names = self.get_existing_rounds_names()

    def get_existing_json_body(self):
        return json.load(
            self.client.get_object(Bucket=S3_BUCKET, Key=OBJECT_KEY)["Body"]
        )

    def get_existing_rounds_names(self):
        print("Getting existing rounds")
        existing_rounds = []
        for round in self.existing_json_body["rounds"]:
            existing_rounds.append(round['round_name'])

        print(f"Existing rounds {existing_rounds}")
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
