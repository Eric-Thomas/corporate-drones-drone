# Corporate Drones Drone

This project is a web scraper that runs every morning at 8 EST and gets all submitted songs in the corporate drones music league https://app.musicleague.com/l/4b82d7c3ca0e4d5db2d9807e3f1da0cc/ and saves it to s3

## How to run locally

- Navigate to `chrome://version` and download the same major version that you are currently running
- [Download a version of chromedriver for your operating system](https://chromedriver.chromium.org/downloads)
- Save this to the root directory of this project with name chromedriver

**Note**: `chromedriver_prod` will be used in production as a headless linux driver. Local development will use a whichever chromedriver you have in the project

- [Install pipenv if you don't already have it](https://pypi.org/project/pipenv/)

#### Install dependencies
```
pipenv shell
pipenv sync --dev
```

#### Export Env variables
This project will use spotify credentials to authenticate with spotify. You must export spotify credentials before running
```
export SPOTIFY_USERNAME={SPOTIFY_USERNAME}
export SPOTIFY_PASSWORD={SPOTIFY_PASSWORD}
```

#### Run main file
`python3 main.py`