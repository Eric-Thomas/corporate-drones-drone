import json

import boto3

S3_BUCKET = 'corporate-drones-music-league'
OBJECT_KEY = 'round_results.json'

class S3Service():

    def __init__(self):
        self.client = boto3.client('s3')
        self.existing_json_body = self.get_existing_json_body()
        self.existing_round_names = self.get_existing_rounds_names()

    def get_existing_json_body(self):
        return json.load(self.client.get_object(Bucket=S3_BUCKET, Key=OBJECT_KEY)['Body'])

    def get_existing_rounds_names(self):
        for round_name in self.existing_json_body:
            print(f"Already have data for {round_name}")
        return self.existing_json_body.keys()

    def write_rounds_results(self, rounds_results):
        # Don't want to overwrite existing rounds so we must include them in final object bytes
        print("Adding new rounds to existing json...")
        rounds_results.update(self.existing_json_body)
        object_bytes = json.dumps(rounds_results).encode('utf-8')
        print(f"Pushing to {S3_BUCKET} with key {OBJECT_KEY}...")
        self.client.put_object(Body=object_bytes, Bucket=S3_BUCKET, Key=OBJECT_KEY)
        print("Successfully pushed to s3")