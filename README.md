# arxiv2slack

## Setup

1. Prepare `.env` values:

   - `SLACK_*`: Create a slack app: https://api.slack.com/apps
   - `OPENAI_API_KEY`: Create an open-api-key: https://platform.openai.com/account/api-keys
   - `ARXIV_QUERY`: Build an query used with arxiv: https://info.arxiv.org/help/api/user-manual.html#query_details

2. Init with `pipenv` (`pipenv sync`) and run `pipenv run python main.py`
